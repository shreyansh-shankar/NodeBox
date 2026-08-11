import json
import os
import subprocess
import sys
import tempfile
import threading
import traceback
from collections import defaultdict, deque
from contextlib import suppress
from time import perf_counter

try:
    from PyQt6.QtCore import QObject, Qt, QThread, QTimer, pyqtSignal
    from PyQt6.QtWidgets import QApplication

    _PYQT_AVAILABLE = True
except Exception:
    _PYQT_AVAILABLE = False

    class QObject:  # type: ignore
        pass

    class QThread:  # type: ignore
        pass

    class QTimer:  # type: ignore
        @staticmethod
        def singleShot(*args, **kwargs):
            return None

    def pyqtSignal(*_args, **_kwargs):  # type: ignore
        class _Sig:
            def connect(self, *a, **k):
                return None

            def emit(self, *a, **k):
                return None

        return _Sig()

    class Qt:  # type: ignore
        class CursorShape:
            WaitCursor = 0

    class QApplication:  # type: ignore
        @staticmethod
        def setOverrideCursor(*_a, **_k):
            return None

        @staticmethod
        def restoreOverrideCursor(*_a, **_k):
            return None


class ExecutionSignals(QObject):
    """Signals for asynchronous node execution completion."""

    execution_completed = pyqtSignal(dict)
    execution_error = pyqtSignal(str)


NODE_TIMEOUT_SECONDS = 30


class NodeExecutionWorker(QObject):
    """Worker class for executing nodes in a separate thread."""

    execution_finished = pyqtSignal(object, dict)
    execution_error = pyqtSignal(object, str)

    def __init__(self, node, code, inputs):
        super().__init__()
        self.node = node
        self.code = code
        self.inputs = inputs

    def run(self):
        try:
            result = _run_node_code_subprocess(self.code, self.inputs)
            self.execution_finished.emit(self.node, result)
        except Exception as e:
            self.execution_error.emit(self.node, str(e))


def _run_node_code_subprocess(
    node_code: str, inputs: dict, timeout: int = NODE_TIMEOUT_SECONDS
):
    temp_file = None
    marker = "___NODEBOX_OUTPUT_MARKER___"

    try:
        temp_file = tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".py", encoding="utf-8"
        )
        temp_name = temp_file.name

        try:
            inputs_json = json.dumps(inputs, default=lambda o: repr(o))
        except Exception:
            safe_inputs = {k: repr(v) for k, v in inputs.items()}
            inputs_json = json.dumps(safe_inputs)

        wrapper = f"""# Auto-generated NodeBox temp script
import json, sys, traceback

try:
    _node_inputs = json.loads({json.dumps(inputs_json)})
except Exception:
    _node_inputs = {{}}

inputs = _node_inputs
globals().update(_node_inputs)

# --- Begin user code ---
"""
        wrapper = wrapper.replace(
            "# --- Begin user code ---\n", "# --- Begin user code ---\noutputs = {}\n"
        )
        temp_file.write(wrapper)
        temp_file.write("\n")
        temp_file.write(node_code)
        temp_file.write("\n\n")
        finalizer = f"""
# --- End user code ---
try:
    _node_outputs = outputs
except Exception:
    _node_outputs = {{}}

def _safe_default(o):
    try:
        return json.loads(json.dumps(o))
    except Exception:
        return repr(o)

print("{marker}")
try:
    print(json.dumps({{'outputs': _node_outputs}}, default=_safe_default))
except Exception:
    safe_outs = {{k: repr(v) for k, v in _node_outputs.items()}}
    print(json.dumps({{'outputs': safe_outs}}))
"""
        temp_file.write(finalizer)
        temp_file.flush()
        temp_file.close()

        try:
            proc = subprocess.run(
                [sys.executable, temp_name],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as te:
            return {
                "stdout": te.stdout or "",
                "stderr": (te.stderr or "")
                + f"\nNode execution timed out after {timeout} seconds.",
                "outputs": {},
                "returncode": -1,
                "error": "timeout",
            }

        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        returncode = proc.returncode

        outputs = {}
        if marker in stdout:
            before, sep, after = stdout.partition(marker)
            user_stdout = before
            json_blob = after.strip()
            parsed = None
            try:
                parsed = json.loads(json_blob)
            except Exception:
                idx = json_blob.find("{")
                if idx != -1:
                    try:
                        parsed = json.loads(json_blob[idx:])
                    except Exception:
                        parsed = None
            if isinstance(parsed, dict) and "outputs" in parsed:
                outputs = parsed.get("outputs", {})
            else:
                outputs = {}
            return {
                "stdout": user_stdout,
                "stderr": stderr,
                "outputs": outputs,
                "returncode": returncode,
            }
        else:
            return {
                "stdout": stdout,
                "stderr": stderr,
                "outputs": {},
                "returncode": returncode,
                "error": "no_outputs_marker",
            }

    except Exception as e:
        tb = traceback.format_exc()
        return {
            "stdout": "",
            "stderr": "",
            "outputs": {},
            "returncode": -1,
            "error": str(e),
            "traceback": tb,
        }

    finally:
        if temp_file is not None:
            try:
                os.remove(temp_name)
            except Exception:
                pass


def run_node_code(node_code: str, inputs: dict, timeout: int = NODE_TIMEOUT_SECONDS):
    return _run_node_code_subprocess(node_code, inputs, timeout=timeout)


def execute_all_nodes(
    nodes,
    connections,
    on_error=None,
    on_node_executed=None,
    signals: ExecutionSignals | None = None,
    on_log=None,
):
    QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

    dependents = defaultdict(list)
    incoming_count = defaultdict(int)
    for conn in connections:
        try:
            src = conn.start_port.node
            dst = conn.end_port.node
            dependents[src].append(dst)
            incoming_count[dst] += 1
        except Exception:
            continue

    ready_queue = deque([node for node in nodes if incoming_count[node] == 0])
    node_outputs = {}
    total_start = perf_counter()
    error_count = 0
    executed_count = 0

    if signals is None:
        try:
            while ready_queue:
                node = ready_queue.popleft()
                exec_env = {}
                for conn in connections:
                    try:
                        if conn.end_port.node == node:
                            src_node = conn.start_port.node
                            if src_node in node_outputs:
                                exec_env.update(node_outputs[src_node])
                    except Exception:
                        continue

                node_start = perf_counter()
                result = None
                try:
                    result = _run_node_code_subprocess(node.code, exec_env)
                except Exception as run_e:
                    tb = traceback.format_exc()
                    result = {
                        "stdout": "",
                        "stderr": str(run_e),
                        "outputs": {},
                        "returncode": -1,
                        "error": "subprocess_failure",
                        "traceback": tb,
                    }

                if result is None:
                    err_text = "No execution result produced"
                    error_count += 1
                    if on_error:
                        with suppress(Exception):
                            on_error(node=node, error=err_text)
                else:
                    rc = result.get("returncode", 0)
                    stderr_text = (result.get("stderr") or "").strip()
                    if rc != 0 or stderr_text:
                        err_text = stderr_text or result.get("error") or "Unknown error"
                        error_count += 1
                        if on_error:
                            with suppress(Exception):
                                on_error(node=node, error=err_text)

                    if on_log:
                        try:
                            std_out = result.get("stdout", "") or ""
                            std_err = result.get("stderr", "") or ""
                            for line in std_out.splitlines():
                                if line.strip():
                                    on_log(line, "stdout")
                            for line in std_err.splitlines():
                                if line.strip():
                                    on_log(line, "stderr")
                        except Exception:
                            pass

                try:
                    outputs_collected = result.get("outputs", {}) if result else {}
                except Exception:
                    outputs_collected = {}

                node_outputs[node] = outputs_collected
                node.outputs = node_outputs[node]

                executed_count += 1
                node_duration = perf_counter() - node_start
                if on_node_executed:
                    with suppress(Exception):
                        on_node_executed(node=node, duration_s=node_duration)

                for dependent in dependents[node]:
                    incoming_count[dependent] -= 1
                    if incoming_count[dependent] == 0:
                        ready_queue.append(dependent)

            total_duration = perf_counter() - total_start
            result_summary = {
                "node_outputs": node_outputs,
                "executed_count": executed_count,
                "error_count": error_count,
                "total_duration_s": total_duration,
                "total_nodes": len(list(nodes)),
            }
            return result_summary
        finally:
            QApplication.restoreOverrideCursor()

    else:
        executing_threads = []
        completed_nodes = set()
        all_done_event = threading.Event()

        def _get_execution_status_class():
            try:
                from nodebox.ui.canvas.node_widget import ExecutionStatus
                return ExecutionStatus
            except Exception:
                try:
                    from automation_manager.node import ExecutionStatus
                    return ExecutionStatus
                except Exception:
                    return None

        def on_node_execution_finished(node, result):
            nonlocal executed_count, error_count
            rc = result.get("returncode", 0)
            stderr_text = result.get("stderr", "") or ""
            ExecutionStatus = _get_execution_status_class()

            if rc != 0 or stderr_text.strip():
                err_text = stderr_text or result.get("error") or "Unknown error"
                if on_error:
                    with suppress(Exception):
                        on_error(node=node, error=err_text)
                try:
                    if hasattr(node, "set_execution_status") and ExecutionStatus:
                        node.set_execution_status(ExecutionStatus.FAILED, err_text)
                except Exception:
                    pass
            else:
                try:
                    if hasattr(node, "set_execution_status") and ExecutionStatus:
                        node.set_execution_status(ExecutionStatus.COMPLETED)
                except Exception:
                    pass

            node_outputs[node] = result.get("outputs", {})
            executed_count += 1
            if rc != 0 or stderr_text.strip():
                error_count += 1

            if on_log:
                try:
                    for line in (result.get("stdout", "") or "").splitlines():
                        if line.strip():
                            on_log(line, "stdout")
                    for line in (result.get("stderr", "") or "").splitlines():
                        if line.strip():
                            on_log(line, "stderr")
                except Exception:
                    pass

            if on_node_executed:
                with suppress(Exception):
                    on_node_executed(node=node, duration_s=0.0)

            completed_nodes.add(node)
            for dependent in dependents[node]:
                incoming_count[dependent] -= 1
                if incoming_count[dependent] == 0 and dependent not in completed_nodes:
                    start_node_execution(dependent)

            if len(completed_nodes) == len(list(nodes)):
                all_done_event.set()

        def on_node_execution_error(node, error_message):
            nonlocal error_count, executed_count
            error_count += 1
            executed_count += 1
            if on_error:
                with suppress(Exception):
                    on_error(node=node, error=error_message)
            completed_nodes.add(node)
            for dependent in dependents[node]:
                incoming_count[dependent] -= 1
                if incoming_count[dependent] == 0 and dependent not in completed_nodes:
                    start_node_execution(dependent)
            if len(completed_nodes) == len(list(nodes)):
                all_done_event.set()

        def start_node_execution(node):
            ExecutionStatus = _get_execution_status_class()
            try:
                if hasattr(node, "set_execution_status") and ExecutionStatus:
                    node.set_execution_status(ExecutionStatus.RUNNING)
            except Exception:
                pass

            local_vars = {}
            for conn in connections:
                try:
                    if conn.end_port.node == node:
                        src_node = conn.start_port.node
                        if src_node in node_outputs:
                            local_vars.update(node_outputs[src_node])
                except Exception:
                    continue

            worker = NodeExecutionWorker(node, node.code, local_vars)
            worker.execution_finished.connect(on_node_execution_finished)
            worker.execution_error.connect(on_node_execution_error)

            thread = QThread()
            worker.moveToThread(thread)
            thread.started.connect(worker.run)
            worker.execution_finished.connect(thread.quit)
            worker.execution_error.connect(thread.quit)
            thread.finished.connect(thread.deleteLater)
            worker.destroyed.connect(thread.deleteLater)

            executing_threads.append((thread, worker))
            thread.start()

        def on_all_execution_complete():
            total_duration = perf_counter() - total_start
            result = {
                "node_outputs": node_outputs,
                "executed_count": executed_count,
                "error_count": error_count,
                "total_duration_s": total_duration,
                "total_nodes": len(list(nodes)),
            }
            QApplication.restoreOverrideCursor()
            try:
                signals.execution_completed.emit(result)
            except Exception:
                pass

        for node in list(ready_queue):
            start_node_execution(node)

        def check_completion():
            if len(completed_nodes) == len(list(nodes)):
                on_all_execution_complete()
            else:
                QTimer.singleShot(100, check_completion)

        QTimer.singleShot(100, check_completion)
        return None


__all__ = [
    "ExecutionSignals",
    "NodeExecutionWorker",
    "run_node_code",
    "execute_all_nodes",
]
