def start_connection(self, port_widget):
    from automation_manager.connection import BezierConnection  # define below

    self.connection_start_port = port_widget
    self.pending_connection = BezierConnection(start_port=port_widget, canvas=self)
    self.update()


def complete_connection(self, target_port):
    if not (self.pending_connection and self.connection_start_port):
        self.cancel_connection()
        return

    start_port = self.connection_start_port

    # Prevent connecting to self
    if start_port == target_port:
        self.cancel_connection()
        return

    # same node
    if start_port.node == target_port.node:
        print("Invalid connection: Cannot connect ports on the same node.")
        self.cancel_connection()
        return

    # same type (input -> input or output -> output)
    if start_port.type == target_port.type:
        print("Invalid connection: Cannot connect ports of same type.")
        self.cancel_connection()
        return

    # passed all checks
    self.pending_connection.end_port = target_port
    self.pending_connection.finalize()
    self.connections.append(self.pending_connection)
    self.pending_connection = None
    self.connection_start_port = None
    self.save_canvas_state()
    self.update()


def cancel_connection(self):
    self.pending_connection = None
    self.connection_start_port = None
    self.update()


def handle_port_click(self, port):
    if self.pending_connection:
        self.complete_connection(port)
    else:
        self.start_connection(port)


def get_port_at(self, pos):
    for node in self.nodes.values():
        for port in [node.input_port, node.output_port]:
            if port.geometry().contains(port.mapFromParent(pos)):
                return port
    return None
