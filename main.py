import os
import sys

import pyperclip as cb

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
from PyQt5.Qt import QTextEdit

from extra_data import ICON_PATH

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'wanztools.brassicatalk.0.0.1'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class BrassicaGUI(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Brassica Talk")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setStyleSheet("background-color: #ffffff")

        self.hbox1 = QHBoxLayout()

        self.textBox = QTextEdit(self)
        self.textBox.setMinimumSize(400, 100)
        self.textBox.setAlignment(Qt.AlignTop)
        self.textBox.textChanged.connect(self.on_text_changed)

        self.hbox1.addWidget(self.textBox)

        self.clearButton = QPushButton("CLEAR")
        self.clearButton.setStyleSheet(
            "background-color: #8acdc2;"
            "border:0px;"
            "border-radius:40px;"
            "color: #ffffff;")
        self.clearButton.setFont(QFont("Consolas", 20, QFont.Bold))
        self.clearButton.setMinimumSize(160, 90)
        self.clearButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.clearButton.clicked.connect(self.on_push_clear_button)

        self.hbox1.addWidget(self.clearButton)

        self.setLayout(self.hbox1)

        self.show()

    def on_text_changed(self):
        cb.copy(self.textBox.toPlainText())

    def on_push_clear_button(self):
        last_text = self.textBox.toPlainText()
        self.textBox.setText("")
        cb.copy(last_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    GUI = BrassicaGUI()
    sys.exit(app.exec_())
