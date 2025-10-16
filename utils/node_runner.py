from collections import defaultdict, deque
from time import perf_counter
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
import tempfile
import subprocess
import sys
import os
import json
import traceback

NODE_TIMEOUT_SECONDS = 30

def _run_node_code_subprocess(node_code: str, inputs: dict, timeout: int = NODE_TIMEOUT_SECONDS):
    """
    Run node_code in a temporary Python file as a subprocess.
    - inputs: dict of variable names -> values to inject into globals().
    - Returns a dict with keys:
        - stdout, stderr, outputs, returncode, error (optional)
    """
    temp_file = None
    marker = "___NODEBOX_OUTPUT_MARKER___"

    try:
        temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py", encoding="utf-8")
        temp_name = temp_file.name

        # Prepare safe JSON of inputs
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

# For backward compatibility
inputs = _node_inputs

# --- Begin user code ---
"""
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
                os.remove(temp_name)
            except Exception:
                pass


def execute_all_nodes(nodes, connections, on_error=None, on_node_executed=None, on_log=None):
    QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
    try:
        dependents = defaultdict(list)
        incoming_count = defaultdict(int)

        for conn in connections:
            src = conn.start_port.node
            dst = conn.end_port.node
            dependents[src].append(dst)
            incoming_count[dst] += 1

        ready_queue = deque([node for node in nodes if incoming_count[node] == 0])
        node_outputs = {}
        total_start = perf_counter()
        error_count = 0
        executed_count = 0

        while ready_queue:
            node = ready_queue.popleft()
            exec_env = {}
            for conn in connections:
                if conn.end_port.node == node:
                    src_node = conn.start_port.node
                    if src_node in node_outputs:
                        exec_env.update(node_outputs[src_node])

            node_start = perf_counter()
            result = None
            try:
                result = _run_node_code_subprocess(node.code, exec_env)
            except Exception as sub_e:
                try:
                    local_exec_env = dict(exec_env)
                    exec(node.code, local_exec_env)
                    result = {
                        "stdout": "",
                        "stderr": "",
                        "outputs": local_exec_env.get("outputs", {}),
                        "returncode": 0,
                    }
                except Exception as exec_e:
                    error_count += 1
                    if on_error:
                        try: on_error(node=node, error=exec_e)
                        except Exception: pass
                    continue

            if result is None:
                err_text = "No execution result produced"
                error_count += 1
                if on_error:
                    try: on_error(node=node, error=err_text)
                    except Exception: pass
            else:
                rc = result.get("returncode", 0)
                stderr_text = result.get("stderr", "") or ""
                if rc != 0 or (stderr_text.strip()):
                    err_text = stderr_text or result.get("error") or "Unknown error"
                    error_count += 1
                    if on_error:
                        try: on_error(node=node, error=err_text)
                        except Exception: pass
                    if on_log:
                        try:
                            for line in result.get("stdout", "").splitlines():
                                on_log(line, "stdout")
                            for line in result.get("stderr", "").splitlines():
                                on_log(line, "stderr")
                        except Exception: pass

            try:
                outputs_collected = result.get("outputs", {}) if result else {}
            except Exception:
                outputs_collected = {}

            node_outputs[node] = outputs_collected
            node.outputs = node_outputs[node]
            executed_count += 1
            node_duration = perf_counter() - node_start
            if on_node_executed:
                try: on_node_executed(node=node, duration_s=node_duration)
                except Exception: pass

            for dependent in dependents[node]:
                incoming_count[dependent] -= 1
                if incoming_count[dependent] == 0:
                    ready_queue.append(dependent)

        total_duration = perf_counter() - total_start
        return {
            "node_outputs": node_outputs,
            "executed_count": executed_count,
            "error_count": error_count,
            "total_duration_s": total_duration,
            "total_nodes": len(list(nodes)),
        }

    finally:
        QApplication.restoreOverrideCursor()
