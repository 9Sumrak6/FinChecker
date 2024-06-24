import socket
import sys
import cmd
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFormLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt


class Mood(cmd.Cmd):
    """Class Mood shows the command line, autocomplete attack command and send commands to server."""

    prompt = ":->"

    def __init__(self, conn, stdin=sys.stdin):
        """Initialize variables."""
        super().__init__(stdin=stdin)
        self.conn = conn

    def do_sayall(self, args):
        """Send message to all players."""
        self.conn.sendall(("sayall " + args + "\n").encode())

    def do_EOF(self, args):
        """End cmd activity."""
        return True


def recieve(conn):
    """Recieve the messages from server in another thread."""
    while conn is not None:
        data = ""
        new = conn.recv(1024)
        new = new.split()
        if new[0] == 'begin':
            if new[1] == 'send_img':
                pass
        elif new[0] == 'end':
            if new[1] == 'send_img':
                pass
        while len(new := conn.recv(1024)) == 1024:
            data += new.decode()

        data += new.decode()
        #print(f"\n{data.strip()}\n{cmd.prompt}{readline.get_line_buffer()}", end='', flush=True)


class LoginFormApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.username = ''

        # Set the window properties (title and initial size)
        self.setWindowTitle("Login Form")
        self.setGeometry(100, 100, 300, 150)  # (x, y, width, height)

        # Create a central widget for the main window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a QFormLayout to arrange the widgets
        form_layout = QFormLayout()

        # Create QLabel and QLineEdit widgets for username
        username_label = QLabel("Username:")
        self.username_field = QLineEdit()

        # Create a QPushButton for login
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)

        # Add widgets to the form layout
        form_layout.addRow(username_label, self.username_field)
        form_layout.addRow(login_button)

        # Set the layout for the central widget
        central_widget.setLayout(form_layout)

    def login(self):
        # Retrieve the username and password entered by the user
        username = self.username_field.text()

# TODO: get reserved usernames from server
        usernames_in_use = ['a']

# TODO: send new username to server
        # Check if the username and password are valid (for demonstration purposes)
        if username not in usernames_in_use:
            self.username = username
            self.close()
            QMessageBox.information(self, "Login Successful", "Welcome, " + username + "!")
        else:
            QMessageBox.warning(self, "Login Failed", "Username already in use. Please try again.")


class ChatApp(QMainWindow):
    def __init__(self, name):
        super().__init__()
        self.username = name

        # set scroll options
        self.scroll = QScrollArea()

        # Set the window properties (title and initial size)
        self.setWindowTitle("Chat Application")
        self.setGeometry(100, 100, 400, 300)  # (x, y, width, height)

        # Create a central widget for the main window
        central_widget = QWidget()
        self.setCentralWidget(self.scroll)

        # Create a QVBoxLayout to arrange the widgets
        layout = QVBoxLayout()

        # Create a QLabel widget to display chat messages
        self.chat_label = QLabel()
        self.chat_label.setWordWrap(True)  # Wrap long messages
        layout.addWidget(self.chat_label)

        # Create a QLineEdit for typing new messages
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...and press Enter key.")
        self.message_input.returnPressed.connect(self.send_message)
        layout.addWidget(self.message_input)

        # Set the layout for the central widget
        central_widget.setLayout(layout)

        # Initialize chat history
        self.chat_history = []

        # Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(central_widget)

    def send_message(self):
        # Get the message from the input field
        message = self.username + ': ' + self.message_input.text()

# TODO: отправить сообщение серверу
        # Append the message to the chat history
        self.chat_history.append(message)

        # Update the chat display
        self.update_chat_display()

        # Clear the input field
        self.message_input.clear()

# TODO: отображать сообщения от других клиентов
    def update_chat_display(self):
        # Display the chat history in the QLabel
        chat_text = "\n".join(self.chat_history)
        self.chat_label.setText(chat_text)

class ButtonsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.start_date = ''
        self.end_date = ''
        self.filename = ''

        # Set the window properties (title and initial size)
        #self.setWindowTitle("Login Form")
        self.setGeometry(100, 100, 300, 150)  # (x, y, width, height)

        # Create a central widget for the main window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QGridLayout()
        self.setLayout(layout)

        # auto complete options
        names = ["correlation table", "stock returns", "dividends", "financials", "balance sheet", "cash flow", "recommendations", "major holders", "institutional holders", "graphics"]
        completer = QCompleter(names)

        # create line edit and add auto complete
        lineedit_label = QLabel("Command")
        self.lineedit = QLineEdit()
        self.lineedit.setCompleter(completer)
        layout.addWidget(self.lineedit, 0, 0)

        # Create a QFormLayout to arrange the widgets
        form_layout = QFormLayout()

        # Create QLabel and QLineEdit widgets for username
        start_date_label = QLabel("Start date:")
        self.start_date_field = QLineEdit()
        self.start_date_field.setPlaceholderText("Date format: YYYY-MM-DD")
        end_date_label = QLabel("End date:")
        self.end_date_field = QLineEdit()
        self.end_date_field.setPlaceholderText("Date format: YYYY-MM-DD")
        filename_label = QLabel("File name:")
        self.filename_field = QLineEdit()

        # Create a QPushButton for login
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submit)

        # Add widgets to the form layout
        form_layout.addRow(lineedit_label, self.lineedit)
        form_layout.addRow(start_date_label, self.start_date_field)
        form_layout.addRow(end_date_label, self.end_date_field)
        form_layout.addRow(filename_label, self.filename_field)
        form_layout.addRow(submit_button)

        # Set the layout for the central widget
        central_widget.setLayout(form_layout)

    def submit(self):
        # Retrieve the username and password entered by the user
        start_date = self.start_date_field.text()
        end_date = self.end_date_field.text()

        # TODO: обработка ошибок формата даты
        correct_dates = ['a']

        # TODO: send request to server
        # Check if the username and password are valid (for demonstration purposes)
        if start_date in correct_dates and end_date in correct_dates:
            self.start_date = start_date
            self.end_date = end_date
            QMessageBox.information(self, "Login Successful", "Welcome, " + "!")
        else:
            QMessageBox.warning(self, "Login Failed", "Username already in use. Please try again.")

def main():
    """Start client."""
    host = "localhost"
    port = 1337
    name = "me"

    app = QApplication(sys.argv)
    window = LoginFormApp()
    window.show()
    app.exec_()
    name = window.username

    window = ChatApp(name)
    window.show()
    app.exec_()

    for i in range(len(sys.argv)):
        if sys.argv[i] == '--host':
            host = 'localhost' if len(sys.argv) < i + 2 else sys.argv[i + 1]
        elif sys.argv[i] == '--port':
            port = 1337 if len(sys.argv) < i + 2 else int(sys.argv[i + 1])
        elif sys.argv[i] == '--name':
            name = "me" if len(sys.argv) < i + 2 else sys.argv[i + 1]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall((name + '\n').encode())
        s.recv(1024)
        print("OK")
        mood = Mood(s)
        mood.cmdloop()
