import socket
import sys
import cmd
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFormLayout, QLabel, QLineEdit, QPushButton, QMessageBox


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
        usernames_in_use = []

# TODO: send new username to server
        # Check if the username and password are valid (for demonstration purposes)
        if username not in usernames_in_use:
            self.username = username
            self.close()
            QMessageBox.information(self, "Login Successful", "Welcome, " + username + "!")
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

    # sys.exit(app.exec_())

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
