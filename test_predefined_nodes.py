"""
Test script to verify the predefined nodes system works correctly
"""

import sys
import os

# Add the parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import predefined nodes system with proper package structure
from predefined.registry import PredefinedNodeRegistry
from predefined.file_reader_node import FileReaderNode  # This will auto-register via decorator

def test_registry():
    """Test that the registry is working"""
    print("Testing PredefinedNodeRegistry...")
    
    # Check if File Reader is registered
    nodes = PredefinedNodeRegistry.get_all_nodes()
    print(f"Registered nodes: {list(nodes.keys())}")
    
    # Check if File Reader node is in the registry
    if "File Reader" in nodes:
        print("✓ File Reader node is registered")
    else:
        print("✗ File Reader node is NOT registered")
        return False
    
    # Get the File Reader node
    file_reader = PredefinedNodeRegistry.get_node("File Reader")
    if file_reader:
        print("✓ Successfully retrieved File Reader node")
    else:
        print("✗ Failed to retrieve File Reader node")
        return False
    
    # Check node data
    node_data = file_reader.get_node_data()
    print(f"\nNode Data:")
    print(f"  Name: {node_data['name']}")
    print(f"  Description: {node_data['description']}")
    print(f"  Has code: {len(node_data['code']) > 0}")
    print(f"  Inputs: {node_data['inputs']}")
    print(f"  Outputs: {list(node_data['outputs'].keys())}")
    
    if node_data['name'] == "File Reader":
        print("✓ Node name is correct")
    else:
        print("✗ Node name is incorrect")
        return False
    
    if len(node_data['code']) > 0:
        print("✓ Node has pre-written code")
    else:
        print("✗ Node has no code")
        return False
    
    if 'file_path' in node_data['inputs']:
        print("✓ Node has correct inputs")
    else:
        print("✗ Node inputs are incorrect")
        return False
    
    if 'content' in node_data['outputs'] and 'error' in node_data['outputs']:
        print("✓ Node has correct outputs")
    else:
        print("✗ Node outputs are incorrect")
        return False
    
    return True

def test_code_execution():
    """Test that the node code works correctly"""
    print("\n\nTesting File Reader Node Code Execution...")
    
    # Create a test file
    test_file = "/tmp/test_nodebox_file.txt"
    test_content = "Hello from NodeBox predefined node!"
    
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    print(f"Created test file: {test_file}")
    
    # Get the node code
    file_reader = PredefinedNodeRegistry.get_node("File Reader")
    node_data = file_reader.get_node_data()
    code = node_data['code']
    
    # Execute the code with inputs
    inputs = {'file_path': test_file}
    outputs = {'content': '', 'error': None}
    
    try:
        exec(code, {'inputs': inputs, 'outputs': outputs, 'os': os})
        print(f"\nExecution successful!")
        print(f"  Content: {outputs['content'][:50]}...")
        print(f"  Error: {outputs['error']}")
        
        if outputs['content'] == test_content:
            print("✓ File content read correctly")
        else:
            print("✗ File content is incorrect")
            return False
        
        if outputs['error'] is None:
            print("✓ No error occurred")
        else:
            print("✗ Error occurred unexpectedly")
            return False
    except Exception as e:
        print(f"✗ Code execution failed: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\nCleaned up test file")
    
    # Test error handling for non-existent file
    print("\n\nTesting error handling for non-existent file...")
    inputs = {'file_path': '/tmp/nonexistent_file_12345.txt'}
    outputs = {'content': '', 'error': None}
    
    try:
        exec(code, {'inputs': inputs, 'outputs': outputs, 'os': os})
        
        if outputs['content'] == '':
            print("✓ Content is empty for non-existent file")
        else:
            print("✗ Content should be empty for non-existent file")
            return False
        
        if outputs['error'] and 'not found' in outputs['error'].lower():
            print("✓ Error message is correct")
        else:
            print("✗ Error message is incorrect")
            return False
    except Exception as e:
        print(f"✗ Error handling failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("PREDEFINED NODES SYSTEM TEST")
    print("=" * 60)
    
    all_passed = True
    
    # Test registry
    if not test_registry():
        all_passed = False
    
    # Test code execution
    if not test_code_execution():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
