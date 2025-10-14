from collections import defaultdict, deque
from time import perf_counter

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

# New imports
import tempfile
import subprocess
import sys
import os
import json
import traceback

# Config: how long to allow a node to run (seconds). Adjust if needed.
NODE_TIMEOUT_SECONDS = 30


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


def execute_all_nodes(nodes, connections, on_error=None, on_node_executed=None):
    """
    Execute all nodes in the workflow with cursor feedback.
    Shows busy cursor during execution.
    """

    # Set busy cursor at the start
    QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

    try:
        print("List of all nodes:\n")
        for node in nodes:
            print(f"Node {node.title}")
            print("-------------------------------------------------------------------")
            print(f"{node.code}")
            print("-------------------------------------------------------------------")

        print("\nList of all connections:\n")
        for conn in connections:
            print(f"Connection: {conn}")
            print(
                f"Start Port: {conn.start_port}, PortNode: {conn.start_port.node.title}, PortType: {conn.start_port.type}"
            )
            print(
                f"End Port: {conn.end_port}, PortNode: {conn.end_port.node.title}, PortType: {conn.end_port.type} \n"
            )

        # ------------------------------
        # Execution Logic
        # ------------------------------

        dependents = defaultdict(list)
        incoming_count = defaultdict(int)

        # Build graph
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

            # Inject upstream outputs into exec_env (used for subprocess inputs or fallback exec)
            exec_env = {}
            for conn in connections:
                if conn.end_port.node == node:
                    src_node = conn.start_port.node
                    if src_node in node_outputs:
                        exec_env.update(node_outputs[src_node])

            # Execute the node's code with injected inputs using subprocess + temp file,
            # with a fallback to exec() if the subprocess helper fails.
            node_start = perf_counter()
            result = None
            try:
                # Prefer subprocess execution for isolation and better error traces
                result = _run_node_code_subprocess(node.code, exec_env)
            except Exception as sub_e:
                # If our helper fails (rare), fallback to in-process exec
                try:
                    local_exec_env = dict(exec_env)  # start with injected inputs
                    exec(node.code, local_exec_env)
                    result = {
                        "stdout": "",
                        "stderr": "",
                        "outputs": local_exec_env.get("outputs", {}),
                        "returncode": 0,
                    }
                except Exception as exec_e:
                    # Both approaches failed -> treat as execution error
                    print(f"❌ Error executing node {node.title}: {exec_e}")
                    error_count += 1
                    if on_error:
                        try:
                            on_error(node=node, error=exec_e)
                        except Exception:
                            pass
                    # Skip scheduling dependents for this failed node
                    continue

            # If subprocess returned a result, handle its return code / stderr
            if result is None:
                # Unexpected: no result produced; treat as error
                err_text = "No execution result produced"
                print(f"❌ Error executing node {node.title}: {err_text}")
                error_count += 1
                if on_error:
                    try:
                        on_error(node=node, error=err_text)
                    except Exception:
                        pass
            else:
                # If subprocess indicated error via returncode or stderr, surface it
                try:
                    rc = result.get("returncode", 0)
                    stderr_text = result.get("stderr", "") or ""
                except Exception:
                    rc = -1
                    stderr_text = "Invalid result structure from executor"

                if rc != 0 or (stderr_text and stderr_text.strip()):
                    err_text = stderr_text or result.get("error") or "Unknown error"
                    print(f"❌ Error executing node {node.title}: {err_text}")
                    error_count += 1
                    if on_error:
                        try:
                            on_error(node=node, error=err_text)
                        except Exception:
                            pass
                    # continue to collect outputs if any

            # Collect outputs from either the subprocess result or fallback exec
            outputs_collected = {}
            try:
                if result and isinstance(result, dict):
                    outputs_collected = result.get("outputs", {}) or {}
                else:
                    outputs_collected = {}
            except Exception:
                outputs_collected = {}

            node_outputs[node] = outputs_collected
            node.outputs = node_outputs[node]

            # Optionally attach stdout/stderr for UI viewing (left commented for now)
            # node.last_stdout = result.get("stdout", "")
            # node.last_stderr = result.get("stderr", "")

            executed_count += 1
            node_duration = perf_counter() - node_start
            print(f"\n✅ Executed node: {node.title}")
            print("Outputs:", node_outputs[node])

            if on_node_executed:
                try:
                    on_node_executed(node=node, duration_s=node_duration)
                except Exception:
                    pass

            # Schedule dependents
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
        # ALWAYS restore cursor when done (success or error)
        QApplication.restoreOverrideCursor()
