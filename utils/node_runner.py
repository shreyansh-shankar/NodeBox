from collections import defaultdict, deque
from time import perf_counter
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication


def execute_all_nodes(nodes, connections, on_error=None, on_node_executed=None):
    """
    Execute all nodes in the workflow with cursor feedback.
    Shows busy cursor during execution.
    """
    
    # Set busy cursor at the start
    QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
    
    try:
        print("List of all nodes:")
        print("\n")
        for node in nodes:
            print(f"Node {node.title}")
            print("-------------------------------------------------------------------")
            print(f"{node.code}")
            print("-------------------------------------------------------------------")

        print("\n")
        print("List of all connections:")
        print("\n")
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

            # Inject upstream outputs
            local_vars = {}
            for conn in connections:
                if conn.end_port.node == node:
                    src_node = conn.start_port.node
                    if src_node in node_outputs:
                        # merge outputs into local_vars
                        local_vars.update(node_outputs[src_node])

            # Execute the node's code with injected inputs
            node_start = perf_counter()
            try:
                exec(node.code, {}, local_vars)
            except Exception as e:
                print(f"❌ Error executing node {node.title}: {e}")
                error_count += 1
                if on_error:
                    try:
                        on_error(node=node, error=e)
                    except Exception:
                        pass
                continue

            # Collect outputs
            node_outputs[node] = local_vars.get("outputs", {})
            node.outputs = node_outputs[node]

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
