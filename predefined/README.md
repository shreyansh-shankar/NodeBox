# Predefined Nodes System

## Overview

The predefined nodes system allows users to drag and drop pre-configured nodes with ready-made functionality onto the canvas. This makes it easier for new users to quickly try out features or test automations without writing code from scratch.

## Architecture

### Directory Structure

```
predefined/
├── __init__.py           # Package initialization and imports
├── base.py              # Base class for all predefined nodes
├── registry.py          # Registry system for managing predefined nodes
└── file_reader_node.py  # First predefined node implementation
```

### Core Components

#### 1. PredefinedNode Base Class (`base.py`)

All predefined nodes inherit from this base class, which defines the standard interface:

- `name`: Display name for the node
- `description`: Brief description of functionality
- `code`: Pre-written Python code
- `inputs`: List of input port names
- `outputs`: Dictionary of output port names and default values

#### 2. Registry System (`registry.py`)

The `PredefinedNodeRegistry` class manages all registered predefined nodes:

- `register(node_class)`: Register a new predefined node
- `get_all_nodes()`: Get all registered nodes
- `get_node(name)`: Get a specific node by name
- `get_node_names()`: Get list of all registered node names

The `@register_predefined_node` decorator automatically registers nodes when they are imported.

#### 3. File Reader Node (`file_reader_node.py`)

The first predefined node implementation:

- **Input**: `file_path` (string) - Path to the file to read
- **Outputs**:
  - `content` (string) - The text content of the file
  - `error` (string or None) - Error message if something goes wrong
- **Features**:
  - Reads file content from the specified path
  - Handles non-existent files gracefully with error messages
  - Handles empty file paths
  - Catches and reports all exceptions

## User Interface Integration

### Sidebar Organization

The node editor sidebar now has two sections:

1. **Predefined Nodes**: All registered predefined nodes appear here
2. **Custom Nodes**: User-created custom nodes

### Drag and Drop

Users can drag any predefined node from the sidebar and drop it onto the canvas. The node will be created with:
- Pre-filled code
- Configured input/output ports
- Ready to use without additional setup

## How to Add New Predefined Nodes

### Step 1: Create a New Node File

Create a new Python file in the `predefined/` directory (e.g., `api_fetcher_node.py`):

```python
from predefined.base import PredefinedNode
from predefined.registry import register_predefined_node

@register_predefined_node
class APIFetcherNode(PredefinedNode):
    name = "API Fetcher"
    description = "Fetches data from an API endpoint"

    code = '''import requests

url = inputs.get('url', '')
try:
    if not url:
        outputs['data'] = None
        outputs['error'] = 'No URL provided'
    else:
        response = requests.get(url)
        response.raise_for_status()
        outputs['data'] = response.json()
        outputs['error'] = None
        print(f'Successfully fetched data from {url}')
except Exception as e:
    outputs['data'] = None
    outputs['error'] = f'Error fetching data: {str(e)}'
    print(f'Error fetching data: {str(e)}')
'''

    inputs = ['url']
    outputs = {
        'data': None,
        'error': None
    }
```

### Step 2: Register the Node

Add the import to `predefined/__init__.py`:

```python
from predefined.api_fetcher_node import APIFetcherNode
```

### Step 3: Test

The node will automatically appear in the sidebar when the application starts.

## Code Execution

When a predefined node is executed, the code has access to:

- `inputs`: Dictionary containing input values from connected nodes
- `outputs`: Dictionary to store output values
- Standard Python libraries (import as needed in the code)

Example execution context:
```python
inputs = {'file_path': '/path/to/file.txt'}
outputs = {'content': '', 'error': None}
# Node code executes here
```

## Error Handling

All predefined nodes should implement proper error handling:

1. **Input Validation**: Check if required inputs are provided
2. **File/Resource Checks**: Verify resources exist before using them
3. **Exception Handling**: Catch and report all exceptions
4. **User Feedback**: Set appropriate error messages in outputs
5. **Console Logging**: Print informative messages for debugging

## Testing

A test script (`test_predefined_nodes.py`) is provided to verify:

- Node registration works correctly
- Node data (name, code, inputs, outputs) is properly configured
- Code execution works as expected
- Error handling functions correctly

Run tests with:
```bash
python test_predefined_nodes.py
```

## Future Enhancements

Potential improvements for the predefined nodes system:

1. **Categorization**: Group nodes by category (I/O, Data Processing, API, etc.)
2. **Search Functionality**: Filter predefined nodes by name or category
3. **More Predefined Nodes**: Add commonly used nodes like:
   - JSON Parser
   - CSV Reader/Writer
   - API Fetcher
   - Text Processor
   - Data Transformer
4. **Node Templates**: Allow users to save custom nodes as reusable templates
5. **Import/Export**: Share predefined nodes between installations
6. **Documentation**: Add help text and examples to each node

## Technical Details

### Integration Points

The predefined nodes system integrates with:

1. **Canvas Widget** (`canvasmanager/canvas_widget.py`):
   - Modified `dropEvent` to recognize predefined nodes
   - Creates nodes with pre-filled code and configured outputs

2. **Node Editor Window** (`automation_manager/node_editor_window.py`):
   - Added "Predefined Nodes" section to sidebar
   - Dynamically loads all registered nodes

3. **Node Widget** (`automation_manager/node.py`):
   - Supports initialization with code and outputs
   - No changes needed to node execution logic

### Extensibility

The system is designed to be easily extensible:

- Adding new nodes requires only creating a new file and importing it
- No modifications to core canvas or node logic needed
- Registry pattern allows dynamic discovery of nodes
- Decorator pattern simplifies registration

## Acceptance Criteria

All acceptance criteria from the original issue have been met:

- ✓ Users can drag predefined nodes from the sidebar onto the canvas
- ✓ File Reader Node works as expected: reads file contents and outputs text
- ✓ No crash if file does not exist (shows error output instead)
- ✓ System is extendable for more predefined nodes later
- ✓ Clear separation between predefined and custom nodes in UI
- ✓ Registration system makes adding new nodes easy
