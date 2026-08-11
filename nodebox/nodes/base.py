"""
Base class for predefined nodes in NodeBox.
"""


class PredefinedNode:
    """
    Base class for all predefined nodes.
    - name: Display name for the node
    - description: Brief description of what the node does
    - code: Pre-written Python code that will be inserted into the node
    - inputs: List of input port names
    - outputs: Dictionary of output port names and default values
    """

    name = "Base Node"
    description = "Base predefined node"
    code = ""
    inputs = []
    outputs = {}

    @classmethod
    def get_node_data(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "code": cls.code,
            "inputs": cls.inputs,
            "outputs": cls.outputs,
        }


__all__ = ["PredefinedNode"]
