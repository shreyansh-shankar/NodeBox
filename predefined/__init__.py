"""
Predefined nodes system for NodeBox
This module provides a registry for predefined nodes with pre-written code.
"""

from predefined.registry import PredefinedNodeRegistry, register_predefined_node
from predefined.base import PredefinedNode

# Import all predefined nodes here
from predefined.file_reader_node import FileReaderNode

# Auto-register all predefined nodes
__all__ = ['PredefinedNodeRegistry', 'register_predefined_node', 'PredefinedNode', 'FileReaderNode']
