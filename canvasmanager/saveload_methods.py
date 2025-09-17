from PyQt6.QtCore import QPointF #type: ignore

import os, json

from automation_manager.node import NodeWidget

def save_canvas_state(self):
        os.makedirs(os.path.expanduser("~/.nodebox/automations"), exist_ok=True)

        nodes_data = []
        for node in self.nodes.values():

            outputs_data = getattr(node, "outputs", {})

            # If it's still a list (old style), convert to dict with None
            if isinstance(outputs_data, list):
                outputs_data = {name: None for name in outputs_data}


            nodes_data.append({
                "id": node.id,
                "name": node.title,
                "position": [int(node.logical_pos.x()), int(node.logical_pos.y())],
                "code": getattr(node, "code", ""),
                "outputs": outputs_data
            })
        
        connections_data = []
        for connection in self.connections:
            from_port = connection.start_port
            to_port = connection.end_port

            if not from_port or not to_port:
                continue
            
            connections_data.append({
                "from_node_id": from_port.node.id,
                "from_port_type": from_port.type,
                "to_node_id": to_port.node.id,
                "to_port_type": to_port.type
            })

    
        automation_data = {
            "nodes": nodes_data,
            "connections": connections_data
        }

        path = os.path.expanduser(f"~/.nodebox/automations/{self.automation_name}.json")
        with open(path, 'w') as f:
            json.dump(automation_data, f, indent=4)


def load_canvas_state(self):
    from automation_manager.connection import BezierConnection

    # Load nodes
    for node_data in self.automation_data.get("nodes", []):
        node_id = node_data["id"]
        title = node_data["name"]
        pos = QPointF(*node_data["position"])
        code = node_data.get("code", "")
        outputs = node_data.get("outputs", {})

        # Backward compatibility: convert list to dict with None
        if isinstance(outputs, list):
            outputs = {name: None for name in outputs}

        node = NodeWidget(title=title, canvas=self, pos=pos)
        node.id = node_id
        self.nodes[node_id] = node
        node.code = code
        node.outputs = outputs
        node.update_position()
        node.show()

    # Load connections
    for conn_data in self.automation_data.get("connections", []):
        from_node = self.nodes.get(conn_data["from_node_id"])
        to_node = self.nodes.get(conn_data["to_node_id"])

        if not from_node or not to_node:
            continue

        from_port = getattr(from_node, f'{conn_data["from_port_type"]}_port', None)
        to_port = getattr(to_node, f'{conn_data["to_port_type"]}_port', None)

        if from_port and to_port:
            connection = BezierConnection(start_port=from_port, canvas=self)
            connection.end_port = to_port
            connection.finalize()
            self.connections.append(connection)

            self.update()