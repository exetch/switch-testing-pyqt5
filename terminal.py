import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPlainTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor

class TerminalWindow(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)

        # Перенаправление stdout в QPlainTextEdit
        sys.stdout = self

    def write(self, text):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def clear_terminal(self):
        self.clear()