import contextlib

from PyQt6.QtWidgets import QDialog


def open_node(self, node):
    from automation_manager.nodeeditor_dialog import NodeEditorDialog

    # Determine inputs for the node: gather variable names from incoming connections.
    # For the basic UI we can show placeholder inputs or actual upstream outputs.
    inputs_dict = {}

    for conn in self.connections:
        if conn.end_port and conn.end_port.node == node:
            upstream_node = conn.start_port.node
            upstream_outputs = getattr(upstream_node, "outputs", {})

            if isinstance(upstream_outputs, dict):
                # Merge all outputs from upstream node
                inputs_dict.update(upstream_outputs)
            elif isinstance(upstream_outputs, list):
                # If upstream only stored names, set placeholder None
                for var in upstream_outputs:
                    inputs_dict[var] = None
            else:
                # Unexpected format, skip
                continue

    # Provide existing code if node has it
    initial_code = getattr(node, "code", "")

    dlg = NodeEditorDialog(
        node=node, inputs=inputs_dict, initial_code=initial_code, parent=self
    )
    if dlg.exec() == QDialog.accepted:
        data = dlg.result_data
        # Apply changes to node:
        node.title = data["title"]
        node.code = data["code"]
        node.output_vars = data["outputs"]
        node.update()  # repaint
        node.update_position()  # reposition ports if needed
        self.save_canvas_state()


def delete_node(self, node):
    """
    Remove the node widget, its ports, and any connections referencing it.
    Save state and repaint.
    """
    # 1) Cancel pending connection if it involves this node
    if self.pending_connection:
        sp = self.pending_connection.start_port
        ep = self.pending_connection.end_port
        if (sp and sp.node == node) or (ep and ep.node == node):
            self.cancel_connection()

    # 2) Remove finalized connections that reference this node
    new_connections = []
    for conn in self.connections:
        sp = getattr(conn, "start_port", None)
        ep = getattr(conn, "end_port", None)
        if (sp and sp.node == node) or (ep and ep.node == node):
            # skip (effectively delete) connections touching this node
            continue
        new_connections.append(conn)
    self.connections = new_connections

    # 3) Delete the node's ports (they are parented to canvas)
    try:
        if hasattr(node, "input_port") and node.input_port:
            node.input_port.deleteLater()
        if hasattr(node, "output_port") and node.output_port:
            node.output_port.deleteLater()
    except Exception:
        pass

    # 4) Remove node from self.nodes dict
    if node.id in self.nodes:
        # node objects are values; self.nodes maps id -> node
        del self.nodes[node.id]

    # 5) If it was selected, clear selection
    if self.selected_node is node:
        self.selected_node = None

    # 6) Delete node widget safely
    node.deleteLater()

    # 7) Persist and redraw
    with contextlib.suppress(Exception):
        self.save_canvas_state()
    self.update()
