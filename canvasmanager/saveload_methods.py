import json
import os
from pathlib import Path

from PyQt6.QtCore import QPointF  # type: ignore
from PyQt6.QtWidgets import QMessageBox  # type: ignore

from automation_manager.node import NodeWidget
from utils.logger import get_logger

logger = get_logger("nodebox.canvas")


def save_canvas_state(self):
    """
    Save the current canvas state to a JSON file.

    Raises:
        Exception: If save operation fails
    """
    try:
        # Ensure automations directory exists
        automations_dir = Path.home() / ".nodebox" / "automations"
        automations_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Automations directory: {automations_dir}")

        # Verify directory was created and is writable
        if not automations_dir.exists():
            raise PermissionError(f"Failed to create directory: {automations_dir}")
        if not os.access(automations_dir, os.W_OK):
            raise PermissionError(f"No write permission for: {automations_dir}")

        nodes_data = []
        for node in self.nodes.values():
            try:
                outputs_data = getattr(node, "outputs", {})

                # If it's still a list (old style), convert to dict with None
                if isinstance(outputs_data, list):
                    outputs_data = dict.fromkeys(outputs_data)
                    logger.debug(f"Converted list outputs to dict for node {node.id}")

                nodes_data.append(
                    {
                        "id": node.id,
                        "name": node.title,
                        "position": [int(node.logical_pos.x()), int(node.logical_pos.y())],
                        "code": getattr(node, "code", ""),
                        "outputs": outputs_data,
                    }
                )
            except Exception as e:
                logger.error(f"Error serializing node {node.id}: {e}")
                # Continue with other nodes instead of failing completely
                continue

        connections_data = []
        for connection in self.connections:
def load_canvas_state(self):
    """
    Load canvas state from automation data.

    Raises:
        Exception: If load operation fails
    """
    from automation_manager.connection import BezierConnection

    try:
        # Load nodes
        loaded_nodes = 0
        for node_data in self.automation_data.get("nodes", []):
            try:
                # Validate node data
                required_fields = ["id", "name", "position"]
                if not all(field in node_data for field in required_fields):
                    logger.warning(f"Skipping node with missing required fields: {node_data}")
                    continue

                node_id = node_data["id"]
                title = node_data["name"]
                position = node_data["position"]
                
                # Validate position data
                if not isinstance(position, list) or len(position) != 2:
                    logger.warning(f"Invalid position data for node {node_id}, using default")
                    position = [0, 0]
                
                pos = QPointF(*position)
                code = node_data.get("code", "")
                outputs = node_data.get("outputs", {})

                # Backward compatibility: convert list to dict with None
                if isinstance(outputs, list):
                    outputs = dict.fromkeys(outputs)
                    logger.debug(f"Converted list outputs to dict for node {node_id}")
                elif not isinstance(outputs, dict):
                    logger.warning(f"Invalid outputs format for node {node_id}, using empty dict")
                    outputs = {}

                node = NodeWidget(title=title, canvas=self, pos=pos)
                node.id = node_id
                self.nodes[node_id] = node
                node.code = code
                node.outputs = outputs
                node.update_position()
                node.show()
                loaded_nodes += 1

            except Exception as e:
                logger.error(f"Error loading node: {e}", exc_info=True)
                # Continue loading other nodes
                continue

        logger.info(f"Loaded {loaded_nodes} nodes successfully")

        # Load connections
        loaded_connections = 0
        for conn_data in self.automation_data.get("connections", []):
            try:
                # Validate connection data
                required_fields = ["from_node_id", "to_node_id", "from_port_type", "to_port_type"]
                if not all(field in conn_data for field in required_fields):
                    logger.warning(f"Skipping connection with missing fields: {conn_data}")
                    continue

                from_node = self.nodes.get(conn_data["from_node_id"])
                to_node = self.nodes.get(conn_data["to_node_id"])

                if not from_node or not to_node:
                    logger.warning(
                        f"Skipping connection - node not found: "
                        f"{conn_data['from_node_id']} -> {conn_data['to_node_id']}"
                    )
                    continue

                from_port = getattr(from_node, f'{conn_data["from_port_type"]}_port', None)
                to_port = getattr(to_node, f'{conn_data["to_port_type"]}_port', None)

                if not from_port or not to_port:
                    logger.warning(
                        f"Skipping connection - port not found: "
                        f"{conn_data['from_port_type']} -> {conn_data['to_port_type']}"
                    )
                    continue

                connection = BezierConnection(start_port=from_port, canvas=self)
                connection.end_port = to_port
                connection.finalize()
                self.connections.append(connection)
                loaded_connections += 1

            except Exception as e:
                logger.error(f"Error loading connection: {e}", exc_info=True)
                # Continue loading other connections
                continue

        logger.info(f"Loaded {loaded_connections} connections successfully")
        self.update()

    except Exception as e:
        logger.error(f"Failed to load canvas state: {e}", exc_info=True)
        if hasattr(self, 'parent') and self.parent():
            QMessageBox.warning(
                self,
                "Load Error",
                f"Some automation data could not be loaded:\n{str(e)}"
            )
        raisemp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            raise

    except Exception as e:
        logger.error(f"Failed to save canvas state: {e}", exc_info=True)
        if hasattr(self, 'parent') and self.parent():
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save automation:\n{str(e)}"
            )
        raise


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
            outputs = dict.fromkeys(outputs)

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
