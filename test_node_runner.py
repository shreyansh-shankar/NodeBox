# test_node_runner.py
from utils.node_runner import _run_node_code_subprocess

# simple node code that uses input 'x' and sets outputs
code = """
# this will raise NameError for undefined var 'z'
y = z + 1
outputs = {'y': y}
"""
res = _run_node_code_subprocess(code, {}, timeout=5)
print(res)
