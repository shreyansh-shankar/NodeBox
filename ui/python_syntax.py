from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt6.QtCore import QRegularExpression

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.rules = []

        # ----- Format styles -----
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(600)

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))

        # ----- Keywords -----
        keywords = [
            "def", "class", "return", "import", "from", "as",
            "if", "elif", "else", "for", "while",
            "try", "except", "with", "pass", "break", "continue",
            "in", "is", "not", "and", "or", "lambda"
        ]

        for kw in keywords:
            pattern = QRegularExpression(rf"\\b{kw}\\b")
            self.rules.append((pattern, keyword_format))

        # ----- Strings -----
        self.rules.append((QRegularExpression(r'".*"'), string_format))
        self.rules.append((QRegularExpression(r"'.*'"), string_format))

        # ----- Comments -----
        self.rules.append((QRegularExpression(r"#.*"), comment_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            match = pattern.globalMatch(text)
            while match.hasNext():
                m = match.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)
