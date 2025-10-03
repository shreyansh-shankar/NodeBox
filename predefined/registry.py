"""
Registry system for predefined nodes
"""


class PredefinedNodeRegistry:
    """
    Registry to store and manage predefined nodes.
    Makes it easy to add new predefined nodes in the future.
    """

    _nodes = {}

    @classmethod
    def register(cls, node_class):
        """
        Register a predefined node class.

        Args:
            node_class: A class that inherits from PredefinedNode
        """
        cls._nodes[node_class.name] = node_class
        return node_class

    @classmethod
    def get_all_nodes(cls):
        """
        Get all registered predefined nodes.

        Returns:
            Dictionary of node_name -> node_class
        """
        return cls._nodes.copy()

    @classmethod
    def get_node(cls, name):
        """
        Get a specific predefined node by name.

        Args:
            name: Name of the predefined node

        Returns:
            The node class or None if not found
        """
        return cls._nodes.get(name)

    @classmethod
    def get_node_names(cls):
        """
        Get list of all registered node names.

        Returns:
            List of node names
        """
        return list(cls._nodes.keys())


def register_predefined_node(node_class):
    """
    Decorator to register a predefined node.

    Usage:
        @register_predefined_node
        class MyNode(PredefinedNode):
            name = "My Node"
            code = "print('Hello')"
    """
    PredefinedNodeRegistry.register(node_class)
    return node_class
