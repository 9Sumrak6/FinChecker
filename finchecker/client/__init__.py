import socket
import sys
import cmd
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFormLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt

class Client(cmd.Cmd):
    prompt = ":->"

    uid = 0
    file_name = dict()

    def __init__(self, conn, stdin=sys.stdin):
        """Initialize variables."""
        super().__init__(stdin=stdin)

        self.conn = conn

    def do_req(self, filename, args):
        file_name[uid] = filename
        uid = (uid + 1) % 1000
        self.conn.sendall((f"req {uid - 1} " + args + "\n").encode())

    def do_graphics(self, args):
        new = args.split()
        Client.file_name[Client.uid] = new[0]
        Client.uid = (Client.uid + 1) % 1000
        self.conn.sendall((f"graphics {Client.uid - 1} " + args + "\n").encode())

    def do_corr(self, filename, args):
        file_name[uid] = filename
        uid = (uid + 1) % 1000
        self.conn.sendall((f"corr {uid - 1} " + args + "\n").encode())

    def do_sayall(self, args):
        """Send message to all players."""
        self.conn.sendall(("sayall " + args + "\n").encode())

    def do_EOF(self, args):
        """End cmd activity."""
        return True


def recieve(conn, client, window):
    """Recieve the messages from server in another thread."""
    files = dict()

    while conn is not None:
        data = ""

        new = conn.recv(1024)
        cmd = new[:3].decode()

        if cmd == 'say':
            msg = new.decode()[4:-1]
            window.get_msg(msg)
        elif cmd == 'beg' or cmd == 'end':
            print(cmd)
            data = new.decode().split()

            if data[0] == 'beg' and data[1] == 'file':
                files[int(data[2])] = open(client.file_name[int(data[2])], "wb")
            elif data[0] == "end" and data[1] == "file":
                files[int(data[2])].close()
                del files[int(data[2])]
        else:
            i1, i2 = 0, 0
            for i in range(100):
                if new[i] == 32 and i1 == 0:
                    i1 = i
                elif new[i] == 32 and i2 == 0:
                    i2 = i
                    break

            file_num = int(new[:i1].decode())
            num = int(new[i1+1:i2].decode()) - 1
            print(new, i2)
            files[file_num].write(new[i2 + 1:])

            for i in range(num):
                new = conn.recv(1024)
                files[file_num].write(new)

        # print(f"\n{data.strip()}\n{cmd.prompt}{readline.get_line_buffer()}", end='', flush=True)

class LoginFormApp(QMainWindow):
    def __init__(self, socket):
        super().__init__()
        self.username = ''
        self.socket = socket

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
        # usernames_in_use = []
        self.socket.sendall((username + '\n').encode())
        print(username)
        ans = self.socket.recv(1024).decode()

        if ans == 'off':
            QMessageBox.warning(self, "Login Failed", "Username already in use. Please try again.")
            self.username = ''
# TODO: send new username to server
        # Check if the username and password are valid (for demonstration purposes)
        # if username not in usernames_in_use:
        else:
            self.username = username
            self.close()
            QMessageBox.information(self, "Login Successful", "Welcome, " + username + "!")


class ChatApp(QMainWindow):
    def __init__(self, name, client):
        super().__init__()
        self.username = name
        self.client = client

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
        self.client.do_sayall(message)
        self.get_msg(message)

        # Clear the input field
        self.message_input.clear()

    def get_msg(self, msg):
        self.chat_history.append(msg)

        # Update the chat display
        self.update_chat_display()

# TODO: отображать сообщения от других клиентов
    def update_chat_display(self):
        # Display the chat history in the QLabel
        chat_text = "\n".join(self.chat_history)
        self.chat_label.setText(chat_text)


def main():
    """Start client."""
    host = "localhost"
    port = 1337
    name = ""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        app = QApplication(sys.argv)

        window = LoginFormApp(s)
        window.show()
        app.exec_()
        name = window.username

        if name == '':
            return

        client = Client(s)
        window = ChatApp(name, client)

        rec = threading.Thread(target=recieve, args=(s, client, window))
        rec.daemon = True
        rec.start()

        window.show()
        client.cmdloop()
        app.exec_()
