import sys
import _thread
import threading

import speech_recognition

from pythonosc import udp_client
import pyperclip as cb

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMenu, QAction, QListWidget, QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QIcon, QFont, QCursor
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.Qt import QTextEdit

from extra_data import ICON_PATH

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'wanztools.brassicatalk.0.0.4'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class BrassicaGUI(QWidget):
    speech_recognized_text = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.osc_client = udp_client.SimpleUDPClient("127.0.0.1", 9000)
        self.osc_prefix_input = "/chatbox/input"

        self.send_auto_clear = True
        self.speech_auto_send = True
        self.talk_button_text = "TALK!"

        self.speech_listening = False
        self.speech_listening_lock = threading.Lock()
        self.stop_listening = None

        self.speech_recognizer = speech_recognition.Recognizer()
        self.speech_microphone = speech_recognition.Microphone()
        # calibrate at start
        with self.speech_microphone as source:
            self.speech_recognizer.adjust_for_ambient_noise(source)

        print(speech_recognition.Microphone.list_microphone_names())

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

        self.talkButton = QPushButton(self.talk_button_text)
        self.talkButton.setStyleSheet(
            "background-color: #de7f6a;"
            "border:0px;"
            "border-radius:40px;"
            "color: #ffffff;")
        self.talkButton.setFont(QFont("Consolas", 20, QFont.Bold))
        self.talkButton.setMinimumSize(160, 80)
        self.talkButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.talkButton.clicked.connect(self.on_push_talk_button)

        # talk button menu
        self.talk_button_menu = QMenu(self)
        self.talk_button_menu.setObjectName("talk_button_menu")

        self.talk_button_action_auto_send = QAction("send after talk", self, checkable=True)
        self.talk_button_action_auto_send.setChecked(True)
        self.talk_button_action_auto_send.triggered.connect(self.toggle_speech_auto_send)

        # self.talk_button_device_list = QListWidget()
        # self.talk_button_device_list.currentItemChanged.connect(self.on_talkbutton_device_changed)
        #
        self.talk_button_menu.addActions([
            self.talk_button_action_auto_send,
        ])

        self.talkButton.setContextMenuPolicy(Qt.CustomContextMenu)
        self.talkButton.customContextMenuRequested.connect(self.on_req_talkbutton_menu)

        self.vbox1.addWidget(self.talkButton)

        self.textBox = QTextEdit(self)
        self.textBox.setFont(QFont("Arial", 18))
        self.textBox.setMinimumSize(400, 100)
        self.textBox.setAlignment(Qt.AlignTop)
        self.textBox.textChanged.connect(self.on_text_changed)

        self.speech_recognized_text.connect(self.handle_speech_recognition_result)

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

        self.send_button_action_auto_clear = QAction("clear after send", self, checkable=True)
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

    def handle_speech_recognition_result(self, recognized_text):
        self.textBox.setText(recognized_text)
        with self.speech_listening_lock:
            self.speech_listening = False
            self.toggle_speech_listening()
        if self.speech_auto_send:
            self.send_content_to_osc()

    def on_push_clear_button(self):
        last_text = self.textBox.toPlainText()
        self.textBox.setText("")
        cb.copy(last_text)
        # set focus back to textBox after any button click
        self.textBox.setFocus()

    def on_push_send_button(self):
        self.send_content_to_osc()
        if self.send_auto_clear:
            self.textBox.setText("")

        # set focus back to textBox after any button click
        self.textBox.setFocus()

    def on_req_sendbutton_menu(self):
        self.send_button_menu.popup(QCursor.pos())
        self.textBox.setFocus()

    def on_push_talk_button(self):
        with self.speech_listening_lock:
            if self.speech_listening:
                return
            self.speech_listening = True
            self.toggle_speech_listening()
            print("[on_push_talk_button] locked")

        def process_speech():
            with self.speech_microphone as source:
                audio = self.speech_recognizer.listen(source)
            print("[process_speech] start")
            recognized_text = ""
            try:
                recognized_text = self.speech_recognizer.recognize_google(audio, language="zh-CN")
                print("[process_speech] recognize completed")
            except speech_recognition.UnknownValueError:
                print("[process_speech] speech_recognition Unknown error")
            except speech_recognition.RequestError as e:
                print(f"[process_speech] request failed: {e}")
            print(f"[process_speech] rec_text: {recognized_text}")
            print("[process_speech] 1")
            print(f"[process_speech] textbox: {self.textBox.toPlainText()}")
            try:
                self.speech_recognized_text.emit(recognized_text)
            except Exception as e:
                print(f"[process_speech] setText error: {e}")
            print("[process_speech] return")

        print("[listen_speech] 2")
        _thread.start_new_thread(process_speech, ())

        self.textBox.setFocus()
        print("[on_push_talk_button] return")

    def on_req_talkbutton_menu(self):
        self.talk_button_menu.popup(QCursor.pos())
        self.textBox.setFocus()

    def on_talkbutton_device_changed(self):
        pass

    def toggle_speech_auto_send(self, auto_send):
        self.speech_auto_send = auto_send
        if auto_send:
            self.talk_button_text = "TALK!"
        else:
            self.talk_button_text = "TALK"
        self.talk_button_sync_text()

        self.textBox.setFocus()

    def talk_button_sync_text(self):
        self.talkButton.setText(self.talk_button_text)

    def toggle_speech_listening(self):
        if self.speech_listening:
            self.talkButton.setText("⚪REC..")
        else:
            self.talk_button_sync_text()

        self.textBox.setFocus()

    def toggle_auto_clear(self, enabled):
        self.send_auto_clear = enabled
        if enabled:
            self.sendButton.setText("SEND!")
        else:
            self.sendButton.setText("SEND")

        # set focus back to textBox
        self.textBox.setFocus()

    def send_content_to_osc(self):
        content = self.textBox.toPlainText()
        self.osc_client.send_message(self.osc_prefix_input, [content, True])
        print(f"[send_content_to_osc] message sent: {content}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    GUI = BrassicaGUI()
    sys.exit(app.exec_())
