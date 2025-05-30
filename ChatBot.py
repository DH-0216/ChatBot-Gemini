import os
import google.generativeai as genai
from PyQt6.QtWidgets import QWidget
from ui.chatbot_ui import Ui_Form
from dotenv import load_dotenv
from PyQt6.QtCore import QThread, pyqtSignal

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

chat = model.start_chat(history=[])

class BotResponseThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, message):
        super().__init__()
        self.message = message

    def run(self):
        response_chunks = chat.send_message(self.message, stream=True)
        response_text = ""
        for chunk in response_chunks:
            response_text += chunk.text
        self.finished.emit(response_text)

class ChatBotGUI(QWidget, Ui_Form): 
    def __init__(self):
        super().__init__()
        self.setupUi(self)  
        self.setWindowTitle("AI-Powered ChatBot")
        self.setGeometry(100, 100, 500, 600)
        self.textEdit.setReadOnly(True)
        self.pushButton.clicked.connect(self.get_response)
        self.lineEdit.returnPressed.connect(self.get_response) 
        self.load_stylesheet("./assets/chat.qss")
        self.response_thread = None
        
        greeting = "Hello! I'm your AI assistant. How can I help you today? 😊"
        self.append_message(greeting, "left")

    
    def show_typing_indicator(self):  
        self.append_message("typing ...", "left")
        self.typing_index = self.textEdit.document().lineCount() - 1

    def remove_typing_indicator(self):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.select(cursor.SelectionType.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()
        
    # This function is triggered when the user presses the send button or hits Enter.
    def get_response(self):
        user_input = self.lineEdit.text().strip()
        if not user_input:
            return
        self.append_message(user_input, "right")
        self.lineEdit.clear()
        self.pushButton.setEnabled(False)
        self.lineEdit.setEnabled(False)
        self.show_typing_indicator()
        self.response_thread = BotResponseThread(user_input)
        self.response_thread.finished.connect(self.handle_bot_reply)
        self.response_thread.start()

    def handle_bot_reply(self, bot_reply):
        self.remove_typing_indicator()
        self.append_message(bot_reply, "left")
        self.pushButton.setEnabled(True)
        self.lineEdit.setEnabled(True)
        self.lineEdit.setFocus()

    # This function appends messages to the textEdit widget with appropriate formatting.
    def append_message(self, message, align):
        if align == "right":
            user_class = "user-message"
            sender = "You"
            formatted_message = f'<p class="{user_class}"><b>{sender}:</b> {message}</p>'
        else:
            user_class = "bot-message"
            sender = "Bot"
            formatted_message = f'<p class="{user_class}" style="color: rgb(52, 11, 236);"><b>{sender}:</b> {message}</p>'
        
        self.textEdit.append(formatted_message)
        self.textEdit.ensureCursorVisible()
        self.lineEdit.setFocus()
     
     
    def load_stylesheet(self, filename):
        try:
            abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), filename))
            with open(abs_path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print(f"Error: {filename} not found!")

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = ChatBotGUI()
    window.show()
    sys.exit(app.exec())


