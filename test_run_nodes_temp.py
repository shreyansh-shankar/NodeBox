# test_run_nodes_temp.py
import importlib.util
import os
import sys

# Ensure repository root is on sys.path so imports work when running this script directly
ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# If PyQt6 is available, ensure a QApplication exists so modules that construct QPixmaps won't error
try:
    from PyQt6.QtWidgets import QApplication

    if QApplication.instance() is None:
        _QAPP = QApplication([])
    else:
        _QAPP = QApplication.instance()
except Exception:
    _QAPP = None

# Import node_runner by file path to avoid package import issues when running this script directly
node_runner_path = os.path.join(ROOT, "utils", "node_runner.py")
spec = importlib.util.spec_from_file_location("node_runner", node_runner_path)
node_runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(node_runner)
execute_all_nodes = node_runner.execute_all_nodes


# --- Dummy Node and Connection Classes ---
class DummyNode:
    _id_counter = 0

    def __init__(self, title, code):
        self.title = title
        self.code = code
        self.outputs = {}
        self.id = DummyNode._id_counter
        DummyNode._id_counter += 1


class DummyPort:
    def __init__(self, node, port_type="input"):
        self.node = node
        self.type = port_type


class DummyConnection:
    def __init__(self, start_node, end_node):
        self.start_port = DummyPort(start_node, "output")
        self.end_port = DummyPort(end_node, "input")


# --- Define nodes ---
node_a = DummyNode("Node A", "outputs = {'x': 42}")
node_b = DummyNode("Node B", "y = inputs.get('x',0) * 2\noutputs = {'y': y}")
node_c = DummyNode("Node C", "outputs = {'z': 100}")
node_d = DummyNode("Node D", "outputs = {'sum': inputs.get('y',0) + inputs.get('z',0)}")

nodes = [node_a, node_b, node_c, node_d]


# --- Define connections ---
connections = [
    DummyConnection(node_a, node_b),
    DummyConnection(node_b, node_d),
    DummyConnection(node_c, node_d),
]


def _on_error(node, error):
    print(f"[on_error] {node.title}: {error}")


def _on_node_executed(node, duration_s):
    print(f"[on_node_executed] {node.title} ({duration_s:.2f}s)")


print("Starting dummy node execution test...\n")
result = execute_all_nodes(
    nodes, connections, on_error=_on_error, on_node_executed=_on_node_executed
)

print("\nFinal node outputs:")
for node in nodes:
    print(f"{node.title}: {node.outputs}")

print("\nExecution summary:")
print(result)
