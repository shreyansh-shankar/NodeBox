"""
File Reader Node - Builtin node that reads file content.
"""

from nodebox.nodes.base import PredefinedNode
from nodebox.nodes.registry import register_predefined_node


@register_predefined_node
class FileReaderNode(PredefinedNode):
    name = "File Reader"
    description = "Reads content from a file and outputs the text"

    code = """import os

file_path = inputs.get('file_path', '')

try:
    if not file_path:
        outputs['content'] = ''
        outputs['error'] = 'No file path provided'
    elif not os.path.exists(file_path):
        outputs['content'] = ''
        outputs['error'] = f'File not found: {file_path}'
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        outputs['content'] = content
        outputs['error'] = None
        print(f'Successfully read file: {file_path}')
except Exception as e:
    outputs['content'] = ''
    outputs['error'] = f'Error reading file: {str(e)}'
    print(f'Error reading file {file_path}: {str(e)}')
"""

    inputs = ["file_path"]
    outputs = {"content": "", "error": None}


__all__ = ["FileReaderNode"]
