import os
import sys

from pythonosc import udp_client
import pyperclip as cb

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMenu, QAction, QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QIcon, QFont, QCursor
from PyQt5.QtCore import Qt
from PyQt5.Qt import QTextEdit

from extra_data import ICON_PATH

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'wanztools.brassicatalk.0.0.3'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class BrassicaGUI(QWidget):

    def __init__(self):
        super().__init__()

        self.osc_client = udp_client.SimpleUDPClient("127.0.0.1", 9000)
        self.osc_prefix_input = "/chatbox/input"

        self.auto_clear = True

        self.init_gui()

    def init_gui(self):
        self.setObjectName("window")
        self.setWindowTitle("Brassica Talk")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setStyleSheet(
            "#window {"
            "   background-color: #ffffff;"
            "}"
        )

        self.hbox1 = QHBoxLayout()

        self.vbox1 = QVBoxLayout()

        self.talkButton = QPushButton("⚪ TALK")
        self.talkButton.setStyleSheet(
            "background-color: #de7f6a;"
            "border:0px;"
            "border-radius:40px;"
            "color: #ffffff;")
        self.talkButton.setFont(QFont("Consolas", 20, QFont.Bold))
        self.talkButton.setMinimumSize(160, 80)
        self.talkButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.talkButton.clicked.connect(self.on_push_talk_button)

        self.vbox1.addWidget(self.talkButton)

        self.textBox = QTextEdit(self)
        self.textBox.setFont(QFont("Arial", 18))
        self.textBox.setMinimumSize(400, 100)
        self.textBox.setAlignment(Qt.AlignTop)
        self.textBox.textChanged.connect(self.on_text_changed)

        self.vbox1.addWidget(self.textBox)

        self.hbox_buttons = QHBoxLayout()

        self.sendButton = QPushButton("SEND!")
        self.sendButton.setStyleSheet(
            "background-color: #6adebb;"
            "border:0px;"
            "border-radius:40px;"
            "color: #ffffff;")
        self.sendButton.setFont(QFont("Consolas", 20, QFont.Bold))
        self.sendButton.setMinimumSize(160, 120)
        self.sendButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.sendButton.clicked.connect(self.on_push_send_button)

        # send button menu
        self.send_button_menu = QMenu(self)
        self.send_button_menu.setObjectName("send_button_menu")

        self.send_button_action_auto_clear = QAction("auto clear after send", self, checkable=True)
        self.send_button_action_auto_clear.setToolTip("auto clear after send")
        self.send_button_action_auto_clear.setChecked(True)
        self.send_button_action_auto_clear.triggered.connect(self.toggle_auto_clear)

        self.send_button_menu.addActions([
            self.send_button_action_auto_clear,
        ])

        self.sendButton.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sendButton.customContextMenuRequested.connect(self.on_req_sendbutton_menu)

        self.hbox_buttons.addWidget(self.sendButton)

        self.clearButton = QPushButton("CLEAR")
        self.clearButton.setStyleSheet(
            "background-color: #e69d6a;"
            "border:0px;"
            "border-radius:40px;"
            "color: #ffffff;")
        self.clearButton.setFont(QFont("Consolas", 20, QFont.Bold))
        self.clearButton.setMinimumSize(160, 120)
        self.clearButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.clearButton.clicked.connect(self.on_push_clear_button)

        self.hbox_buttons.addWidget(self.clearButton)

        self.vbox1.addLayout(self.hbox_buttons)

        self.hbox1.addLayout(self.vbox1)

        self.setLayout(self.hbox1)

        self.show()

    def on_text_changed(self):
        cb.copy(self.textBox.toPlainText())

    def on_push_clear_button(self):
        last_text = self.textBox.toPlainText()
        self.textBox.setText("")
        cb.copy(last_text)
        # set focus back to textBox after any button click
        self.textBox.setFocus()

    def on_push_send_button(self):
        self.send_content_to_osc(self.textBox.toPlainText())
        if self.auto_clear:
            self.textBox.setText("")
        # set focus back to textBox after any button click
        self.textBox.setFocus()

    def on_req_sendbutton_menu(self):
        self.send_button_menu.popup(QCursor.pos())

    def on_push_talk_button(self):
        self.textBox.setFocus()

    def toggle_auto_clear(self, enabled):
        self.auto_clear = enabled
        if enabled:
            self.sendButton.setText("SEND!")
        else:
            self.sendButton.setText("SEND")

        # set focus back to textBox
        self.textBox.setFocus()

    def send_content_to_osc(self, content):
        self.osc_client.send_message(self.osc_prefix_input, [content, True])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    GUI = BrassicaGUI()
    sys.exit(app.exec_())
