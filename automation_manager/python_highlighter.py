from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt5.QtCore import QRegExp

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(PythonHighlighter, self).__init__(parent)

        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#569CD6"))

        keywords = [
            "def", "class", "import", "from", "return",
            "if", "elif", "else", "for", "while", "try",
            "except", "with", "as", "pass", "break", "continue"
        ]

        self.rules = [
            (QRegExp(r"\b" + word + r"\b"), self.keyword_format)
            for word in keywords
        ]

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            i = pattern.indexIn(text)
            while i >= 0:
                length = pattern.matchedLength()
                self.setFormat(i, length, fmt)
                i = pattern.indexIn(text, i + length)
