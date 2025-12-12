# NodeBox - Bugs and Improvements Documentation

> **Purpose**: This document tracks identified bugs, potential issues, and improvement opportunities in the NodeBox codebase. This serves as a comprehensive audit for code quality and reliability.
> 
> **Last Updated**: December 5, 2025

---

## 🐛 Critical Bugs

### 1. Missing Error Handling in main.py Font Loading
**File**: `main.py` (Lines 32-34)
**Severity**: Medium
**Description**: Font files are loaded without error handling. If font files are missing, the application will crash.

**Current Code**:
```python
QFontDatabase.addApplicationFont(resource_path("assets/fonts/Poppins-Regular.ttf"))
QFontDatabase.addApplicationFont(resource_path("assets/fonts/Poppins-Medium.ttf"))
QFontDatabase.addApplicationFont(resource_path("assets/fonts/Poppins-SemiBold.ttf"))
```

**Issue**: 
- No try-except block to handle missing font files
- Application crashes if fonts are not found
- No fallback mechanism

**Proposed Fix**: Add error handling with graceful degradation to system fonts

---

### 2. QSS File Loading Without Error Handling
**File**: `main.py` (Lines 38-40)
**Severity**: Medium
**Description**: Dark theme stylesheet is loaded without error handling.

**Current Code**:
```python
qss_file = resource_path("qss/dark.qss")
with open(qss_file, "r") as file:
    app.setStyleSheet(file.read())
```

**Issue**:
- File I/O operation without try-except
- Application crashes if QSS file is missing or corrupted
- No fallback to default styling

**Proposed Fix**: Add error handling with fallback to basic dark theme

---

### 3. Ollama Process Cleanup Race Condition
**File**: `main.py` (Lines 50-56)
**Severity**: Low
**Description**: Potential zombie process if cleanup fails

**Current Code**:
```python
if ollama_process:
    ollama_process.terminate()
    try:
        ollama_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        ollama_process.kill()
```

**Issue**:
- No verification that process was actually killed
- No cleanup of child processes
- Process might remain as zombie

**Proposed Fix**: Add process verification and proper cleanup

---

### 4. Missing File Existence Check in Canvas Save
**File**: `canvasmanager/saveload_methods.py` (Line 9)
**Severity**: Low
**Description**: Directory creation might fail silently in some edge cases

**Current Code**:
```python
os.makedirs(os.path.expanduser("~/.nodebox/automations"), exist_ok=True)
```

**Issue**:
- No error handling for permission issues
- No verification that directory was actually created
- Could fail on restricted filesystems

**Proposed Fix**: Add error handling and verification

---

### 5. Node Runner Exception Swallowing
**File**: `utils/node_runner.py` (Lines 272-276)
**Severity**: Medium
**Description**: Malformed connections are silently ignored

**Current Code**:
```python
for conn in connections:
    try:
        src = conn.start_port.node
        dst = conn.end_port.node
        dependents[src].append(dst)
        incoming_count[dst] += 1
    except Exception:
        # ignore malformed connections
        continue
```

**Issue**:
- Generic exception catching hides real errors
- No logging of ignored connections
- Users get no feedback about why their connections don't work

**Proposed Fix**: Add specific exception handling and logging

---

### 6. Unsafe Type Conversions in Node Loading
**File**: `canvasmanager/saveload_methods.py` (Lines 62-65)
**Severity**: Medium
**Description**: List to dict conversion without validation

**Current Code**:
```python
# Backward compatibility: convert list to dict with None
if isinstance(outputs, list):
    outputs = dict.fromkeys(outputs)
```

**Issue**:
- No validation of list contents
- Could create invalid outputs dictionary
- No error handling for edge cases

**Proposed Fix**: Add validation and error handling

---

## ⚠️ Potential Issues

### 7. Resource Path Resolution
**File**: Multiple files using `resource_path()`
**Severity**: Medium
**Description**: Resource path resolution might fail when running from different contexts

**Impact**:
- PyInstaller bundled apps might not find resources
- Development vs production environment inconsistencies
- Path resolution errors on different OS

**Recommendation**: Add comprehensive path validation and fallback mechanisms

---

### 8. Thread Safety in Node Execution
**File**: `utils/node_runner.py`
**Severity**: Medium
**Description**: No explicit thread safety mechanisms for concurrent node execution

**Impact**:
- Potential race conditions in node_outputs dictionary
- Unsafe shared state access
- Could cause intermittent execution failures

**Recommendation**: Add thread locks or use thread-safe data structures

---

### 9. Memory Leak in Debug Console
**File**: `features/debug_console.py` (Line 64)
**Severity**: Low
**Description**: Deque with maxlen=500 could accumulate memory over long sessions

**Current Code**:
```python
self.logs = deque(maxlen=500)
```

**Impact**:
- Long-running sessions might accumulate large logs
- No cleanup mechanism
- Memory usage grows unbounded for complex log entries

**Recommendation**: Add periodic cleanup and memory monitoring

---

### 10. Subprocess Timeout Handling
**File**: `utils/node_runner.py`
**Severity**: High
**Description**: 30-second timeout might be insufficient for complex operations

**Impact**:
- Long-running AI model inference might timeout
- Data processing tasks fail prematurely
- No way for users to configure timeout

**Recommendation**: Make timeout configurable per node

---

## 🔧 Code Quality Issues

### 11. Inconsistent Error Message Format
**Files**: Multiple
**Severity**: Low
**Description**: Error messages use different formats and styles

**Examples**:
- `"Error: Ollama is not installed or not in PATH."`
- `f'Error reading file {file_path}: {str(e)}'`
- `"No execution result produced"`

**Recommendation**: Create standardized error message format and centralized error handling

---

### 12. Hardcoded Paths
**Files**: Multiple
**Severity**: Medium
**Description**: Several hardcoded paths that should be configurable

**Examples**:
- `~/.nodebox/automations`
- `/usr/local/bin/ollama`
- Asset paths

**Recommendation**: Move to configuration file or constants module

---

### 13. Missing Type Hints
**Files**: Most Python files
**Severity**: Low
**Description**: Limited use of type hints makes code harder to maintain

**Impact**:
- Reduced IDE support
- Harder to catch type-related bugs
- Poor documentation for API users

**Recommendation**: Add comprehensive type hints using Python 3.10+ syntax

---

### 14. Insufficient Logging
**Files**: Multiple
**Severity**: Medium
**Description**: Print statements instead of proper logging

**Examples**:
```python
print("Error: Ollama is not installed or not in PATH.")
print(f'Successfully read file: {file_path}')
```

**Recommendation**: Implement proper logging framework with levels

---

### 15. No Input Validation
**Files**: Multiple node implementations
**Severity**: High
**Description**: User inputs are not validated before processing

**Impact**:
- Potential security vulnerabilities
- Injection attacks possible
- Data corruption risk

**Recommendation**: Add comprehensive input validation layer

---

## 🚀 Performance Improvements

### 16. Inefficient Graph Traversal
**File**: `utils/node_runner.py`
**Severity**: Medium
**Description**: Multiple iterations over connections list

**Impact**:
- O(n²) complexity in some cases
- Slow for large workflows
- Redundant computations

**Recommendation**: Optimize with better data structures (adjacency lists)

---

### 17. Font Loading on Every Start
**File**: `main.py`
**Severity**: Low
**Description**: Fonts are loaded every time app starts

**Impact**:
- Slower startup time
- Redundant I/O operations

**Recommendation**: Cache font loading or check if already loaded

---

### 18. Synchronous File I/O
**File**: Multiple files
**Severity**: Medium
**Description**: File operations block the main thread

**Impact**:
- UI freezes during save/load
- Poor user experience
- Application appears unresponsive

**Recommendation**: Move file I/O to background threads

---

## 📊 Architecture Improvements

### 19. Tight Coupling
**Severity**: Medium
**Description**: Many components are tightly coupled

**Examples**:
- Canvas directly manipulates node internals
- UI components access data layer directly
- No clear separation of concerns

**Recommendation**: Implement proper MVC/MVP pattern with clear boundaries

---

### 20. Missing Dependency Injection
**Severity**: Low
**Description**: Hard-coded dependencies make testing difficult

**Recommendation**: Implement dependency injection for better testability

---

## 🧪 Testing Gaps

### 21. No Unit Tests
**Severity**: Critical
**Description**: No unit test framework or tests

**Impact**:
- No automated verification
- Regression bugs easily introduced
- Difficult to refactor safely

**Recommendation**: Add pytest framework with comprehensive test coverage

---

### 22. No Integration Tests
**Severity**: High
**Description**: No integration tests for workflows

**Recommendation**: Add integration tests for common automation scenarios

---

### 23. No CI/CD Pipeline
**Severity**: Medium
**Description**: No automated testing in CI

**Recommendation**: Add GitHub Actions for automated testing

---

## 📝 Documentation Issues

### 24. Missing Docstrings
**Files**: Most modules
**Severity**: Medium
**Description**: Many functions lack docstrings

**Recommendation**: Add comprehensive docstrings following Google or NumPy style

---

### 25. No API Documentation
**Severity**: Medium
**Description**: No generated API documentation

**Recommendation**: Use Sphinx to generate API docs from docstrings

---

### 26. Outdated Comments
**Files**: Multiple
**Severity**: Low
**Description**: Some comments don't match current implementation

**Recommendation**: Audit and update all comments

---

## 🔐 Security Concerns

### 27. Arbitrary Code Execution
**File**: `utils/node_runner.py`
**Severity**: Critical
**Description**: User code is executed without sandboxing

**Impact**:
- Users can execute arbitrary Python code
- File system access unrestricted
- Network access unrestricted
- Could be exploited maliciously

**Recommendation**: Implement code sandboxing or security warnings

---

### 28. No Input Sanitization
**Files**: Multiple
**Severity**: High
**Description**: User inputs used in file paths and commands without sanitization

**Impact**:
- Path traversal attacks possible
- Command injection possible
- Data exfiltration risk

**Recommendation**: Add input sanitization and validation

---

### 29. Credentials in Environment
**Severity**: Medium
**Description**: No secure credential storage mechanism

**Recommendation**: Implement secure credential storage (keyring)

---

## 🎨 UI/UX Improvements

### 30. No Dark/Light Theme Toggle
**Severity**: Low
**Description**: Only dark theme available

**Recommendation**: Add theme switcher

---

### 31. Missing Keyboard Shortcuts Documentation
**Severity**: Low
**Description**: No visible keyboard shortcuts reference

**Recommendation**: Add keyboard shortcuts help dialog

---

### 32. No Undo/Redo
**Severity**: Medium
**Description**: Canvas operations can't be undone

**Recommendation**: Implement undo/redo stack

---

## 📈 Metrics and Monitoring

### 33. No Error Tracking
**Severity**: Medium
**Description**: No centralized error tracking

**Recommendation**: Add error tracking and analytics (optional, privacy-respecting)

---

### 34. No Performance Metrics
**Severity**: Low
**Description**: Limited performance monitoring

**Recommendation**: Enhance performance monitor with more metrics

---

## 🔄 Backward Compatibility

### 35. Breaking Changes in Outputs Format
**File**: `canvasmanager/saveload_methods.py`
**Severity**: Low
**Description**: List to dict migration might break old automations

**Impact**:
- Old automation files might not load correctly
- Users lose their work

**Recommendation**: Add migration tool and better backward compatibility

---

## Summary Statistics

- **Total Issues Identified**: 35
- **Critical**: 2
- **High**: 4
- **Medium**: 17
- **Low**: 12

## Priority Matrix

### Immediate (Next PR)
1. Missing error handling in main.py (Issues #1, #2)
2. Input validation (Issue #15)
3. Logging framework (Issue #14)
4. Exception handling improvements (Issue #5)

### Short Term (Following PRs)
1. Unit testing framework (Issue #21)
2. Type hints (Issue #13)
3. Security improvements (Issues #27, #28)
4. Performance optimizations (Issues #16, #18)

### Medium Term
1. Architecture improvements (Issue #19)
2. UI/UX enhancements (Issues #30, #32)
3. Documentation (Issues #24, #25)
4. CI/CD pipeline (Issue #23)

### Long Term
1. Code sandboxing (Issue #27)
2. Advanced features
3. Internationalization
4. Plugin system

---

## Contributing

If you'd like to work on fixing any of these issues:

1. Check if an issue exists on GitHub
2. Comment on the issue to claim it
3. Create a branch: `fix/issue-description`
4. Submit PR referencing this document
5. Ensure tests pass (once test framework is added)

## Notes

- This document should be updated as issues are fixed
- New issues should be added as they are discovered
- Each fix should reference the issue number from this document
