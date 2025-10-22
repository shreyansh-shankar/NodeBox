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

from PyQt6.QtCore import QObject, Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication


class ExecutionSignals(QObject):
    """Signals for asynchronous node execution completion"""
    execution_completed = pyqtSignal(dict)  # result dict
    execution_error = pyqtSignal(str)  # error message


# Config: how long to allow a node to run (seconds). Adjust if needed.
NODE_TIMEOUT_SECONDS = 30


class NodeExecutionWorker(QObject):
    """Worker class for executing nodes in a separate thread"""
    execution_finished = pyqtSignal(object, dict)  # node, result
    execution_error = pyqtSignal(object, str)  # node, error_message

    def __init__(self, node, code, inputs):
        super().__init__()
        self.node = node
        self.code = code
        self.inputs = inputs
        self.cancelled= False

    def run(self):
        """Execute the node code and emit results"""
        if self.cancelled:
            self.execution_error.emit(self.node, "Execution cancalled")
            return
        try:
            result = _run_node_code_subprocess(self.code, self.inputs, timeout=300)
            self.execution_finished.emit(self.node, result)
        except Exception as e:
            self.execution_error.emit(self.node, str(e))


def _run_node_code_subprocess(node_code: str, inputs: dict, timeout: int = NODE_TIMEOUT_SECONDS):
    """
    Run node_code in a temporary Python file as a subprocess.
    - inputs: dict of variable names -> values to inject into globals().
    - Returns a dict with keys:
        - stdout: string printed by the user's code (everything before the marker)
        - stderr: string from the subprocess stderr
        - outputs: dict parsed from the JSON the wrapper prints (or {} fallback)
        - returncode: subprocess return code (int)
        - error (optional): string describing a local helper error (not subprocess stderr)
    """
    temp_file = None
    marker = "___NODEBOX_OUTPUT_MARKER___"  # unique marker to separate logs from outputs JSON

    try:
        # Create a temp file (not delete-on-close because subprocess will read it)
        temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py", encoding="utf-8")
        temp_name = temp_file.name

        # ✅ DEBUG: show file creation path
        print(f"[DEBUG] Created temp file for node execution: {temp_name}")

        # Prepare inputs JSON safely
        try:
            inputs_json = json.dumps(inputs, default=lambda o: repr(o))
        except Exception:
            # fallback: convert all values to repr
            safe_inputs = {k: repr(v) for k, v in inputs.items()}
            inputs_json = json.dumps(safe_inputs)

        # Compose the temp script content:
        wrapper = f"""# Auto-generated temp script for NodeBox node execution
import json, sys, traceback
try:
    _node_inputs = json.loads({json.dumps(inputs_json)})
except Exception:
    _node_inputs = {{}}
globals().update(_node_inputs)

# --- Begin user node code ---
"""

        # Write wrapper + user code + finalizer
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

        # Run subprocess
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
                "stderr": (te.stderr or "") + f"\nNode execution timed out after {timeout} seconds.",
                "outputs": {},
                "returncode": -1,
                "error": "timeout",
            }

        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        returncode = proc.returncode

        # Extract JSON output after marker
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
        return {"stdout": "", "stderr": "", "outputs": {}, "returncode": -1, "error": str(e), "traceback": tb}

    finally:
        if temp_file is not None:
            try:
                # ✅ DEBUG: show file deletion
                print(f"[DEBUG] Deleting temp file: {temp_name}")
                os.remove(temp_name)
            except Exception:
                pass


def execute_all_nodes(nodes, connections, on_error=None, on_node_executed=None, signals=None):
    """
    Execute all nodes in the workflow asynchronously using threading.
    Shows busy cursor during execution but allows UI updates.
    Uses signals for completion instead of blocking.

    Args:
        nodes: List of node objects to execute
        connections: List of connection objects
        on_error: Callback for individual node errors
        on_node_executed: Callback for individual node completion
        signals: ExecutionSignals object for completion notifications
    """

    # Reset all nodes to idle status before starting
    for node in nodes:
        if hasattr(node, 'reset_execution_status'):
            node.reset_execution_status()

    # Set busy cursor at the start
    QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

    try:
        # print("List of all nodes:")
        # print("\n")
        # for node in nodes:
        #     print(f"Node {node.title}")
        #     print("-------------------------------------------------------------------")
        #     print(f"{node.code}")
        #     print("-------------------------------------------------------------------")

        # print("\n")
        # print("List of all connections:")
        # print("\n")
        # for conn in connections:
        #     print(f"Connection: {conn}")
        #     start_port = conn.start_port
        #     print(
        #         f"Start Port: {start_port}, PortNode: {start_port.node.title}, "
        #         f"PortType: {start_port.type}"
        #     )
        #     print(
        #         f"End Port: {conn.end_port}, PortNode: {conn.end_port.node.title}, PortType: {conn.end_port.type} \n"
        #     )

        # ------------------------------
        # Asynchronous Execution Logic using Threads
        # ------------------------------

        dependents = defaultdict(list)
        incoming_count = defaultdict(int)
        node_outputs = {}
        executing_threads = []
        completed_nodes = set()

        # Build graph
        for conn in connections:
            src = conn.start_port.node
            dst = conn.end_port.node
            dependents[src].append(dst)
            incoming_count[dst] += 1

        ready_queue = deque([node for node in nodes if incoming_count[node] == 0])
        total_start = perf_counter()
        error_count = 0
        executed_count = 0

        # Event to signal when all nodes are done
        all_done_event = threading.Event()

        def on_node_execution_finished(node, result):
            """Called when a node finishes execution"""
            nonlocal executed_count, error_count, completed_nodes, node_outputs

            # Check if execution was successful
            if result.get("returncode", 0) != 0 or result.get("stderr"):
                err_text = result.get("stderr") or result.get("error") or "Unknown error"
                print(f"❌ Error executing node {node.title}: {err_text}")
                error_count += 1

                # Set node status to failed
                if hasattr(node, 'set_execution_status'):
                    from automation_manager.node import ExecutionStatus
                    node.set_execution_status(ExecutionStatus.FAILED, err_text)

                # Call error callback if provided
                if on_error:
                    with suppress(Exception):
                        on_error(node=node, error=err_text)
            else:
                # Set node status to completed on success
                if hasattr(node, 'set_execution_status'):
                    from automation_manager.node import ExecutionStatus
                    node.set_execution_status(ExecutionStatus.COMPLETED)

            # Collect outputs
            node_outputs[node] = result.get("outputs", {})
            executed_count += 1

            print(f"\n✅ Executed node: {node.title}")
            print("Outputs:", node_outputs[node])

            if on_node_executed:
                with suppress(Exception):
                    on_node_executed(node=node, duration_s=0)  # We don't track individual duration in threads

            # Schedule dependents
            completed_nodes.add(node)
            for dependent in dependents[node]:
                incoming_count[dependent] -= 1
                if incoming_count[dependent] == 0 and dependent not in completed_nodes:
                    start_node_execution(dependent)

            # Check if all nodes are done
            if len(completed_nodes) == len(nodes):
                all_done_event.set()

        def on_node_execution_error(node, error_message):
            """Called when a node execution fails"""
            nonlocal error_count, executed_count, completed_nodes
            print(f"❌ Error executing node {node.title}: {error_message}")
            error_count += 1

            # Set node status to failed
            if hasattr(node, 'set_execution_status'):
                from automation_manager.node import ExecutionStatus
                node.set_execution_status(ExecutionStatus.FAILED, error_message)

            if on_error:
                with suppress(Exception):
                    on_error(node=node, error=error_message)

            completed_nodes.add(node)
            executed_count += 1

            # Schedule dependents (even on error, some might still run)
            for dependent in dependents[node]:
                incoming_count[dependent] -= 1
                if incoming_count[dependent] == 0 and dependent not in completed_nodes:
                    start_node_execution(dependent)

            # Check if all nodes are done
            if len(completed_nodes) == len(nodes):
                all_done_event.set()

        def start_node_execution(node):
            """Start execution of a single node in a separate thread"""
            print(f"[DEBUG] Starting threaded execution for node '{node.title}'")

            # Set node status to running
            if hasattr(node, 'set_execution_status'):
                from automation_manager.node import ExecutionStatus
                node.set_execution_status(ExecutionStatus.RUNNING)

            # Inject upstream outputs
            local_vars = {}
            for conn in connections:
                if conn.end_port.node == node:
                    src_node = conn.start_port.node
                    if src_node in node_outputs:
                        # merge outputs into local_vars
                        local_vars.update(node_outputs[src_node])

            # Create worker and thread
            worker = NodeExecutionWorker(node, node.code, local_vars)
            worker.execution_finished.connect(on_node_execution_finished)
            worker.execution_error.connect(on_node_execution_error)

            thread = QThread()
            worker.moveToThread(thread)

            # Connect thread start/finish
            thread.started.connect(worker.run)
            worker.execution_finished.connect(thread.quit)
            worker.execution_error.connect(thread.quit)
            thread.finished.connect(thread.deleteLater)
            worker.destroyed.connect(thread.deleteLater)

            executing_threads.append((thread, worker))
            thread.start()

        def on_all_execution_complete():
            """Called when all nodes have finished executing"""
            # Note: Threads clean themselves up automatically via deleteLater()
            # Don't try to quit or wait on threads that may already be deleted

            total_duration = perf_counter() - total_start

            result = {
                "node_outputs": node_outputs,
                "executed_count": executed_count,
                "error_count": error_count,
                "total_duration_s": total_duration,
                "total_nodes": len(list(nodes)),
            }

            # Restore cursor and emit completion signal
            QApplication.restoreOverrideCursor()
            try:
                if signals:
                    signals.execution_completed.emit(result)
            except Exception as e:
                print(f"Error emitting completion signal: {e}")
                import traceback
                traceback.print_exc()
            print(f"✅ All nodes execution completed in {total_duration:.2f}s")

        # Start initial nodes (those with no dependencies)
        for node in ready_queue:
            start_node_execution(node)

        # Set up completion monitoring without blocking
        def check_completion():
            if len(completed_nodes) == len(nodes):
                on_all_execution_complete()
            else:
                # Check again after a short delay
                QTimer.singleShot(100, check_completion)

        # Start monitoring completion
        QTimer.singleShot(100, check_completion)

        # Return immediately - completion will be signaled asynchronously
        return None

    finally:
        # ALWAYS restore cursor when done (success or error)
        QApplication.restoreOverrideCursor()
