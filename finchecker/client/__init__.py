"""Init file with all functionality for client."""

import socket
import sys
import cmd
import threading

import xml.etree.ElementTree as ET
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFormLayout, QLabel, QLineEdit, QPushButton, \
    QMessageBox, QVBoxLayout, QScrollArea, QGridLayout, QCompleter
from PyQt5.QtCore import Qt
from datetime import date


def update_stat(filename, tree, root, tag):
    # tree = ET.parse(filename)
    # root = tree.getroot()

    for cmd in root.findall(tag):
        cmd.text = str(int(cmd.text) + 1)
        cmd.set('updated', 'yes')

    tree.write(filename)


def reset_stat(filename, tree, root, tag, clear=False):
    for cmd in root:
        if clear:
            cmd.text = "0"
        cmd.set('updated', 'no')

    tree.write(filename)


class Client(cmd.Cmd):
    """Class for sending requests to server with ability of using cmd instead of GUI."""

    prompt = ":->"

    uid = 0
    file_name = dict()

    full_name = {
        'corr' : 'correlation_table',
        'stock' : 'stock_returns',
        'dividends' : 'dividends',
        'fin' : 'financials',
        'balance' : 'balance_sheet',
        'cash' : 'cash_flow',
        'recom' : 'recommendations',
        'm_hold' : 'major_holders',
        'i_hold' : 'institutional_holders',
        'graphics' : 'graphics',
        'sayall' : 'sayall'
    }

    def __init__(self, conn, stdin=sys.stdin):
        """
        Initialize variables.

        :param conn: socket to server
        :param stdin: input stream
        """

        super().__init__(stdin=stdin)

        self.conn = conn

        self.cur_path_xml = str(Path(__file__).parent.resolve()) + '/stat.xml'

        self.tree = ET.parse(self.cur_path_xml)
        self.root = self.tree.getroot()

    def do_req(self, cmd, filename, args=''):
        """
        Send request to server.

        :param cmd: type of command
        :param filename: name of file where it will be stored
        :param args: arguments for executing command
        """
        Client.file_name[Client.uid] = filename
        Client.uid = (Client.uid + 1) % 1000

        update_stat(self.cur_path_xml, self.tree, self.root, Client.full_name[cmd])

        self.conn.sendall((f"{cmd} {Client.uid - 1} " + args + "\n").encode())

    # def do_graphics(self, args):
    #     new = args.split()
    #     Client.file_name[Client.uid] = new[0]
    #     Client.uid = (Client.uid + 1) % 1000
    #     self.conn.sendall((f"graphics {Client.uid - 1}\n").encode())

    def do_sayall(self, msg):
        """
        Send message for users.

        :param msg: message
        """
        update_stat(self.cur_path_xml, self.tree, self.root, "sayall")
        self.conn.sendall(("sayall " + msg + "\n").encode())

    def do_EOF(self, args):
        """End client activity."""
        reset_stat(self.cur_path_xml, self.tree, self.root, False)
        return True


def recieve(conn, client, window):
    """
    Recieve the messages from server in another thread.
    
    :param conn: socket to server
    :param client: class Client
    :param window: GUI window 
    """
    files = dict()

    while conn is not None:
        new = conn.recv(1024)
        cmd = new[:3].decode()

        if cmd == 'say':
            msg = new.decode()[4:-1]
            window.get_msg(msg)
        elif cmd == 'beg' or cmd == 'end':
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


def check_data(inp: str) -> bool:
    if len(inp) != 10:
        return False
    inp = inp.split('-')
    if len(inp) != 3:
        return False
    if not inp[0].isdigit() or not inp[1].isdigit() or not inp[2].isdigit():
        return False
    current_date = str(date.today()).split('-')
    year, month, day = int(inp[0]), int(inp[1]), int(inp[2])
    curr_y, curr_m, curr_d = int(current_date[0]), int(current_date[1]), int(current_date[2])
    if year < 1900 or year > curr_y:
        return False
    if month < 0 or month > 12 or year == curr_y and month > curr_m:
        return False
    if day < 0 or day > 31 or year == curr_y and month == curr_m and day > curr_d:
        return False
    if month == 2 and (day > 29 or abs(year - 2000) % 4 != 0 and day == 29):
        return False
    if month in [4, 6, 9, 11] and day == 31:
        return False
    return True


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

        # get reserved usernames from server
        self.socket.sendall((username + '\n').encode())
        print(username)
        ans = self.socket.recv(1024).decode()

        if ans == 'off':
            QMessageBox.warning(self, "Login Failed", "Username already in use. Please try again.")
            self.username = ''
        # send new username to server
        # Check if the username and password are valid (for demonstration purposes)
        # if username not in usernames_in_use:
        else:
            self.username = username
            self.close()
            QMessageBox.information(self, "Login Successful", "Welcome, " + username + "!")


class Parametres(QWidget):
    def __init__(self, cmd):
        super().__init__()
        self.start_date = ''
        self.end_date = ''
        self.filename = ''
        self.cmd = cmd

        only_ticker = ["financials", "balance sheet", "cash flow", "recommendations", "major holders",
                       "institutional holders", "graphics"]
        other = ["correlation table", "stock returns", "dividends"]

        # Set the window properties (title and initial size)
        self.setWindowTitle("Parametres for " + cmd)
        self.setGeometry(100, 100, 300, 150)  # (x, y, width, height)

        layout = QGridLayout()
        self.setLayout(layout)

        # auto complete options
        names = ["AMAZON", "GOOGLE"]
        completer = QCompleter(names)

        # create line edit and add auto complete
        lineedit_label = QLabel("Company")
        self.lineedit = QLineEdit()
        self.lineedit.setCompleter(completer)
        layout.addWidget(lineedit_label, 0, 0)
        layout.addWidget(self.lineedit, 0, 1)

        start_date_label = QLabel("Start date:")
        self.start_date_field = QLineEdit()
        self.start_date_field.setPlaceholderText("Date format: YYYY-MM-DD")
        end_date_label = QLabel("End date:")
        self.end_date_field = QLineEdit()
        self.end_date_field.setPlaceholderText("Date format: YYYY-MM-DD")
        filename_label = QLabel("File name:")
        self.filename_field = QLineEdit()

        if cmd in other:
            layout.addWidget(start_date_label, 1, 0)
            layout.addWidget(self.start_date_field, 1, 1)
            layout.addWidget(end_date_label, 2, 0)
            layout.addWidget(self.end_date_field, 2, 1)
        layout.addWidget(filename_label, 3, 0)
        layout.addWidget(self.filename_field, 3, 1)

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submit)
        layout.addWidget(submit_button)

    def submit(self):
        # Retrieve the username and password entered by the user
        start_date = self.start_date_field.text()
        end_date = self.end_date_field.text()
        self.filename = self.filename_field.text()

        # TODO: check tickers and maybe filename
        # TODO: send request to server
        # Check if the username and password are valid (for demonstration purposes)
        if check_data(start_date) and check_data(end_date):
            self.start_date = start_date
            self.end_date = end_date
            QMessageBox.information(self, self.cmd + "made Successfully", "Check file " + self.filename + " in folder")
        else:
            QMessageBox.warning(self, "Fail", "Incorrect date format. Please try again.")


class ChatApp(QMainWindow):
    def __init__(self, name, client):
        super().__init__()
        self.username = name
        self.client = client
        self.cmd = ''

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
        new_layout = QGridLayout()
        self.setLayout(new_layout)

        # auto complete options
        names = ["correlation table", "stock returns", "dividends", "financials", "balance sheet", "cash flow",
                 "recommendations", "major holders", "institutional holders", "graphics"]
        completer = QCompleter(names)

        lineedit_label = QLabel("Command")
        self.lineedit = QLineEdit()
        self.lineedit.setCompleter(completer)
        new_layout.addWidget(self.lineedit, 0, 0)

        # Create a QPushButton for login
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submit)

        # Create a QLabel widget to display chat messages
        self.chat_label = QLabel()
        self.chat_label.setWordWrap(True)  # Wrap long messages
        layout.addWidget(self.chat_label)

        # Create a QLineEdit for typing new messages
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...and press Enter key.")
        self.message_input.returnPressed.connect(self.send_message)
        layout.addWidget(self.message_input)

        # Add widgets to the form layout
        layout.addWidget(self.lineedit)
        layout.addWidget(submit_button)

        # Set the layout for the central widget
        central_widget.setLayout(layout)

        # Initialize chat history
        self.chat_history = []

        # Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(central_widget)

    def submit(self):
        self.cmd = self.lineedit.text()
        self.w = Parametres(self.cmd)
        self.w.show()

    def send_message(self):
        # Get the message from the input field
        message = self.username + ': ' + self.message_input.text()

        # отправить сообщение серверу
        self.client.do_sayall(message)
        self.get_msg(message)

        # Clear the input field
        self.message_input.clear()

    def get_msg(self, msg):
        self.chat_history.append(msg)

        # Update the chat display
        self.update_chat_display()

    # отображать сообщения от других клиентов
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
        # client.cmdloop()
        app.exec_()
