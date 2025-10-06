# NodeBox - Code Reference

This document provides a high-level overview of the NodeBox source code structure, key modules, and their purpose.

```markdown
---
### `automation_manager/nodeeditor_dialog.py`

This module contains the UI for the Node Editor dialog window.

- **`class NodeEditorDialog(QDialog)`**:
  - **Description:** A responsive dialog window for editing a node's code. It uses a `QSplitter` layout and handles running the code and saving the results.
```

```markdown
---
### `canvasmanager/canvas_manager.py`

This module manages the main canvas where users build their automation workflows.

- **`class CanvasManager`**:
  - **Description:** Handles all the logic for the canvas, such as adding nodes, connecting them, and managing the overall state of the workflow.
```

```markdown
---
### `main.py`

This is the main entry point for the NodeBox application.

- **Purpose:** It initializes the main application window and starts the program's event loop.
```
