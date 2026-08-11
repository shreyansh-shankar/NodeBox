"""
Registry system for predefined nodes in NodeBox.
"""


class PredefinedNodeRegistry:
    """Registry to store and manage predefined nodes."""

    _nodes = {}

    @classmethod
    def register(cls, node_class):
        cls._nodes[node_class.name] = node_class
        return node_class

    @classmethod
    def get_all_nodes(cls):
        return cls._nodes.copy()

    @classmethod
    def get_node(cls, name):
        return cls._nodes.get(name)

    @classmethod
    def get_node_names(cls):
        return list(cls._nodes.keys())


def register_predefined_node(node_class):
    PredefinedNodeRegistry.register(node_class)
    return node_class


__all__ = ["PredefinedNodeRegistry", "register_predefined_node"]
