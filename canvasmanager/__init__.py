from .canvas_nodemethods import delete_node, open_node
from .canvas_widget import CanvasWidget
from .ports_handler import (
    cancel_connection,
    complete_connection,
    get_port_at,
    handle_port_click,
    start_connection,
)
from .saveload_methods import load_canvas_state, save_canvas_state

CanvasWidget.open_node = open_node
CanvasWidget.delete_node = delete_node
CanvasWidget.save_canvas_state = save_canvas_state
CanvasWidget.load_canvas_state = load_canvas_state
CanvasWidget.start_connection = start_connection
CanvasWidget.complete_connection = complete_connection
CanvasWidget.cancel_connection = cancel_connection
CanvasWidget.handle_port_click = handle_port_click
CanvasWidget.get_port_at = get_port_at

__all__ = ["CanvasWidget"]
