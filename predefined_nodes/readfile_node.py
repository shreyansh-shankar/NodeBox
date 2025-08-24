from ui.node import NodeWidget

from PyQt6.QtWidgets import QPushButton, QFileDialog, QTextEdit, QVBoxLayout

class ReadFileNode(NodeWidget):
    def __init__(self, canvas, pos=None):
        super().__init__("Read File", canvas, pos)

        # UI Elements for this node
        self.button = QPushButton("Select File")
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)

        # Layout inside the node
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.text_display)
        self.setLayout(layout)

        # Connect button click to file reader
        self.button.clicked.connect(self.load_file)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Text File", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.text_display.setText(content)
