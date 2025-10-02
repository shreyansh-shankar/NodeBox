"""
Base class for predefined nodes
"""


class PredefinedNode:
    """
    Base class for all predefined nodes.
    Each predefined node must define:
    - name: Display name for the node
    - description: Brief description of what the node does
    - code: Pre-written Python code that will be inserted into the node
    - inputs: List of input port names (optional)
    - outputs: Dictionary of output port names and their default values (optional)
    """

    name = "Base Node"
    description = "Base predefined node"
    code = ""
    inputs = []
    outputs = {}

    @classmethod
    def get_node_data(cls):
        """
        Returns a dictionary containing all the node's configuration data.
        """
        return {
            "name": cls.name,
            "description": cls.description,
            "code": cls.code,
            "inputs": cls.inputs,
            "outputs": cls.outputs
        }
