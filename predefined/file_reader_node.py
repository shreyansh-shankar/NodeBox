"""
File Reader Node - Predefined node that reads file content
"""

from predefined.base import PredefinedNode
from predefined.registry import register_predefined_node


@register_predefined_node
class FileReaderNode(PredefinedNode):
    """
    File Reader Node - Reads content from a file

    Input: file_path (string) - Path to the file to read
    Output: content (string) - The text content of the file
    """

    name = "File Reader"
    description = "Reads content from a file and outputs the text"
    
    # Pre-written code that will be inserted into the node
    code = """import os

# Get the file path from inputs
file_path = inputs.get('file_path', '')

try:
    # Check if file path is provided
    if not file_path:
        outputs['content'] = ''
        outputs['error'] = 'No file path provided'
    # Check if file exists
    elif not os.path.exists(file_path):
        outputs['content'] = ''
        outputs['error'] = f'File not found: {file_path}'
    else:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        outputs['content'] = content
        outputs['error'] = None
        print(f'Successfully read file: {file_path}')
except Exception as e:
    # Handle any other errors
    outputs['content'] = ''
    outputs['error'] = f'Error reading file: {str(e)}'
    print(f'Error reading file {file_path}: {str(e)}')
"""

    # Define inputs and outputs
    inputs = ['file_path']
    outputs = {
        'content': '',
        'error': None
    }
