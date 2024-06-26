"""Init file with all functionality for client."""

import socket
import sys
import os
import cmd
import threading
import gettext
import seaborn as sns
import pandas as pd
import locale
from matplotlib import pyplot as plt
from PIL import Image

import xml.etree.ElementTree as ET
from ..common import companies
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFormLayout, QLabel, QLineEdit, QPushButton, \
    QMessageBox, QVBoxLayout, QScrollArea, QGridLayout, QCompleter
from PyQt5.QtCore import Qt
from datetime import date


PO_PATH = str(os.path.dirname(__file__) + '/../po')
LOCALES = {
    "ru_RU.UTF-8": gettext.translation("gui", PO_PATH, ["ru"]),
    "en_US.UTF-8": gettext.NullTranslations(),
}

# GEN_PATH = str(os.path.dirname(__file__) + '/../../generates')


def indent(elem, level=0):
    """
    Make indent in xml files.

    :param elem: watching element
    :param level: level of element
    """
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def create_xml(path, full_name):
    """Create xml pattern for statistics."""
    if Path(path).is_file():
        return True

    root = ET.Element("statistics")

    for i in full_name:
        field = ET.SubElement(root, "_".join(i.split()))
        field.text = "0"
        field.set('updated', 'no')

    tree = ET.ElementTree(root)
    indent(root)
    tree.write(path, encoding="utf-8", xml_declaration=True)

    return True


def update_stat(filename, tree, root, tag):
    """
    Update users activity.

    :param filename: name of file
    :param tree: tree of xml
    :param root: root of tree
    :param tag: tag of updating field
    """
    for command in root.findall(tag):
        command.text = str(int(command.text) + 1)
        command.set('updated', 'yes')

    tree.write(filename)


def get_stat(filename, tree, root, tag):
    """
    Get user activity by tag.

    :param filename: name of file
    :param tree: tree of xml
    :param root: root of tree
    :param tag: tag of updating field
    """
    for command in root.findall(tag):
        return int(command.text)


def reset_stat(filename, tree, root, clear=False):
    """
    Reset users activity.

    :param filename: name of file
    :param tree: tree of xml
    :param root: root of tree
    :param clear: clear all fields(True) or reset only updated info(False)
    """
    for command in root:
        if clear:
            command.text = "0"
        command.set('updated', 'no')

    tree.write(filename)


class Client(cmd.Cmd):
    """Class for sending requests to server with ability of using cmd instead of GUI."""

    prompt = ":->"

    uid = 0
    file_name = dict()

    full_name = {
        'correlation table': 'corr',
        'stock returns': 'stock',
        'dividends': 'dividends',
        'financials': 'fin',
        'balance sheet': 'balance',
        'cash flow': 'cash',
        'recommendations': 'recom',
        'major holders': 'm_hold',
        'institutional holders': 'i_hold',
        'graphics': 'graphics',
        'sayall': 'sayall',
        'predict': 'predict'
    }

    keys = [
        'correlation_table',
        'stock_returns',
        'dividends',
        'financials',
        'balance_sheet',
        'cash_flow',
        'recommendations',
        'major_holders',
        'institutional_holders',
        'graphics',
        'sayall',
        'predict'
    ]

    def __init__(self, conn, lang='ru_RU.UTF-8', stdin=sys.stdin):
        """
        Initialize variables.

        :param conn: socket to server
        :param lang: language
        :param stdin: input stream
        """
        super().__init__(stdin=stdin)

        self.conn = conn
        self.locale = LOCALES[lang]
        self.cur_path_xml = str(Path(__file__).parent.resolve()) + '/stat.xml'

        create_xml(self.cur_path_xml, Client.full_name)

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

        update_stat(self.cur_path_xml, self.tree, self.root, "_".join(cmd.split()))
        self.conn.sendall((f"{Client.full_name[cmd]} {Client.uid - 1} " + args + "\n").encode())

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

    def do_vis(self):
        """Visualise users activity."""
        values = []

        for i in Client.keys:
            values.append(get_stat(self.cur_path_xml, self.tree, self.root, i))

        df = pd.DataFrame({'commands': Client.keys, 'num': values})

        plt.figure(figsize=(16, 9))

        plt.title(self.locale.gettext('Statistics of requests'), fontsize=15)

        sns.barplot(df, x=df.country, y=df.num)

        plt.xlabel(self.locale.gettext('Request'))
        plt.ylabel(self.locale.gettext('Number of requests'))

        plt.grid(True)

        if not Path('generates').is_dir():
            Path('generates').mkdir(parents=True, exist_ok=True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('generates/statistics.jpg')

        im = Image.open("generates/statistics.jpg")
        im.show()

    def do_EOF(self):
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
                if not Path('generates').is_dir():
                    Path('generates').mkdir(parents=True, exist_ok=True)

                files[int(data[2])] = open('generates/' + client.file_name[int(data[2])] + data[3], "wb")
            elif data[0] == "end" and data[1] == "file":
                files[int(data[2])].close()
                del files[int(data[2])]

                if data[3] != '.csv':
                    im = Image.open('generates/' + client.file_name[int(data[2])] + data[3])
                    im.show()
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

            files[file_num].write(new[i2 + 1:])

            for i in range(num):
                new = conn.recv(1024)
                files[file_num].write(new)

        # print(f"\n{data.strip()}\n{cmd.prompt}{readline.get_line_buffer()}", end='', flush=True)


def check_data(inp: str) -> bool:
    """Check the correctness of entered date."""
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
    """Authorization."""

    def __init__(self, socket, lang='ru_RU.UTF-8'):
        """
        Create visualization of LoginFormApp.

        :param socket: socket
        :param lang: locale language
        """
        super().__init__()
        self.username = ''
        self.socket = socket
        self.locale = LOCALES[lang]

        # Set the window properties (title and initial size)
        self.setWindowTitle(self.locale.gettext("Login Form"))
        self.setGeometry(100, 100, 300, 150)  # (x, y, width, height)

        # Create a central widget for the main window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a QFormLayout to arrange the widgets
        form_layout = QFormLayout()

        # Create QLabel and QLineEdit widgets for username
        username_label = QLabel(self.locale.gettext("Username:"))
        self.username_field = QLineEdit()
        password_label = QLabel(self.locale.gettext("Password:"))
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.Password)

        # Create a QPushButton for login
        login_button = QPushButton(self.locale.gettext("Login"))
        login_button.clicked.connect(self.login)

        # Add widgets to the form layout
        form_layout.addRow(username_label, self.username_field)
        form_layout.addRow(password_label, self.password_field)
        form_layout.addRow(login_button)

        # Set the layout for the central widget
        central_widget.setLayout(form_layout)

    def login(self):
        """Send username and password to server and recieve respond."""
        # Retrieve the username and password entered by the user
        username = self.username_field.text()
        password = self.password_field.text()

        # get reserved usernames from server
        self.socket.sendall(('usr ' + username + ' /pswd/ ' + password + '\n').encode())
        # self.socket.sendall((password + '\n').encode())
        print(username)
        ans = self.socket.recv(1024).decode()

        if ans == 'off':
            QMessageBox.warning(self, self.locale.gettext("Login Failed"),
                                self.locale.gettext("Invalid username or password. Please try again."))
            self.username = ''
            self.password = ''
        # send new username to server
        # Check if the username and password are valid (for demonstration purposes)
        # if username not in usernames_in_use:
        else:
            self.username = username
            self.password = password
            self.close()
            QMessageBox.information(self, self.locale.gettext("Login Successful"),
                                    self.locale.gettext("Welcome, ") + username + "!")


class Parameters(QWidget):
    """Send parameters to server."""

    def __init__(self, cmd, client, lang='ru_RU.UTF-8'):
        """
        Create visualization of parameters.

        :param cmd: command from ChatApp
        :param client: object of Client class
        :param lang: locale language
        """
        super().__init__()
        self.cmd = cmd
        self.client = client
        self.locale = LOCALES[lang]
        self.start_date = ''
        self.end_date = ''
        self.filename = ''
        self.days = ''
        self.only_ticker = []
        self.other = []
        self.extra = []

        only_ticker = ["financials", "balance sheet", "cash flow", "recommendations", "major holders",
                       "institutional holders"]
        other = ["correlation table", "stock returns", "dividends", "graphics"]
        extra = ["predict"]
        for ticker in only_ticker:
            self.only_ticker.append(self.locale.gettext(ticker))
        for ticker in other:
            self.other.append(self.locale.gettext(ticker))
        for ticker in extra:
            self.extra.append(self.locale.gettext(ticker))

        # Set the window properties (title and initial size)
        self.setWindowTitle(self.locale.gettext("Parameters for ") + cmd)
        self.setGeometry(100, 100, 300, 150)  # (x, y, width, height)

        layout = QGridLayout()
        self.setLayout(layout)

        # auto complete options
        names = companies.keys()
        completer = QCompleter(names)

        # create line edit and add auto complete
        lineedit_label = QLabel(self.locale.gettext("Company:"))
        self.lineedit_field = QLineEdit()
        self.lineedit_field.setCompleter(completer)
        layout.addWidget(lineedit_label, 0, 0)
        layout.addWidget(self.lineedit_field, 0, 1)

        start_date_label = QLabel(self.locale.gettext("Start date:"))
        self.start_date_field = QLineEdit()
        self.start_date_field.setPlaceholderText(self.locale.gettext("Date format: YYYY-MM-DD"))
        end_date_label = QLabel(self.locale.gettext("End date:"))
        self.end_date_field = QLineEdit()
        self.end_date_field.setPlaceholderText(self.locale.gettext("Date format: YYYY-MM-DD"))
        days_label = QLabel(self.locale.gettext("The number of days to predict:"))
        self.days_field = QLineEdit()
        filename_label = QLabel(self.locale.gettext("File name:"))
        self.filename_field = QLineEdit()

        if cmd in self.other or cmd in self.extra:
            layout.addWidget(start_date_label, 1, 0)
            layout.addWidget(self.start_date_field, 1, 1)
            layout.addWidget(end_date_label, 2, 0)
            layout.addWidget(self.end_date_field, 2, 1)
        if cmd in self.extra:
            layout.addWidget(days_label, 3, 0)
            layout.addWidget(self.days_field, 3, 1)
        layout.addWidget(filename_label, 4, 0)
        layout.addWidget(self.filename_field, 4, 1)

        submit_button = QPushButton(self.locale.gettext("Submit"))
        submit_button.clicked.connect(self.submit)
        layout.addWidget(submit_button)

    def submit(self):
        """Send parameters to server."""
        # Retrieve the username and password entered by the user
        if self.cmd in self.other or self.cmd in self.extra:
            start_date = self.start_date_field.text()
            end_date = self.end_date_field.text()
        self.lineedit = self.lineedit_field.text()
        self.filename = self.filename_field.text()
        if self.cmd in self.extra:
            days = self.days_field.text()

        # TODO: check tickers and maybe filename
        # TODO: send request to server
        # Check if the username and password are valid (for demonstration purposes)
        if self.cmd in self.extra:
            self.start_date = start_date
            self.end_date = end_date
            self.days = days
            self.client.do_req(self.cmd, self.filename,
                               f"{self.lineedit} {self.start_date} {self.end_date} {self.days}")
            QMessageBox.information(self, self.cmd + self.locale.gettext("made Successfully"),
                                    self.locale.gettext("Check file ") + self.filename +
                                    self.locale.gettext(" in folder"))
        elif self.cmd not in self.other:
            self.client.do_req(self.cmd, self.filename, self.lineedit)
            QMessageBox.information(self, self.cmd + self.locale.gettext("made Successfully"),
                                    self.locale.gettext("Check file ") + self.filename +
                                    self.locale.gettext(" in folder"))
        elif check_data(start_date) and check_data(end_date):
            self.start_date = start_date
            self.end_date = end_date
            self.client.do_req(self.cmd, self.filename, f"{self.lineedit} {self.start_date} {self.end_date}")
            QMessageBox.information(self, self.cmd + self.locale.gettext("made Successfully"),
                                    self.locale.gettext("Check file ") + self.filename +
                                    self.locale.gettext(" in folder"))
        else:
            QMessageBox.warning(self, self.locale.gettext("Fail"),
                                self.locale.gettext("Incorrect date format. Please try again."))


class ChatApp(QMainWindow):
    """Chat application for multiple users and client-server communication."""

    def __init__(self, name, client, lang='ru_RU.UTF-8'):
        """
        Create visualization of functionality.

        :param name: client name
        :param client: object of Client class
        :param lang: locale language
        """
        super().__init__()
        self.locale = LOCALES[lang]
        self.username = name
        self.client = client
        self.cmd = ''

        # set scroll options
        self.scroll = QScrollArea()

        # Set the window properties (title and initial size)
        self.setWindowTitle(self.locale.gettext("Chat"))
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
                 "recommendations", "major holders", "institutional holders", "graphics", "predict", "statistics"]
        locale_names = []
        for name in names:
            locale_names.append(self.locale.gettext(name))

        completer = QCompleter(locale_names)
        self.lineedit = QLineEdit()
        self.lineedit.setPlaceholderText(self.locale.gettext("Command"))
        self.lineedit.setCompleter(completer)
        new_layout.addWidget(self.lineedit, 0, 1)

        # Create a QPushButton for login
        submit_button = QPushButton(self.locale.gettext("Submit"))
        submit_button.clicked.connect(self.submit)

        # Create a QLabel widget to display chat messages
        self.chat_label = QLabel()
        self.chat_label.setWordWrap(True)  # Wrap long messages
        layout.addWidget(self.chat_label)

        # Create a QLineEdit for typing new messages
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText(self.locale.gettext("Type your message here...and press Enter key."))
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
        """Get command from client and show parameters."""
        self.cmd = self.lineedit.text()
        if self.cmd == "statistics":
            self.client.do_vis()
            return
        self.w = Parameters(self.cmd, self.client)
        self.w.show()

    def send_message(self):
        """Send message to all clients."""
        # Get the message from the input field
        message = self.username + ': ' + self.message_input.text()

        # отправить сообщение серверу
        self.client.do_sayall(message)
        self.get_msg(message)

        # Clear the input field
        self.message_input.clear()

    def get_msg(self, msg):
        """
        Recieve new message and update display.

        :param msg: message from client
        """
        self.chat_history.append(msg)

        # Update the chat display
        self.update_chat_display()

    # отображать сообщения от других клиентов
    def update_chat_display(self):
        """Update chat after recieving new messages."""
        # Display the chat history in the QLabel
        chat_text = "\n".join(self.chat_history)
        self.chat_label.setText(chat_text)


LANGUAGES = {'en': 'en_US.UTF-8',
             'ru': 'ru_RU.UTF-8',
             }


def main():
    """Start client."""
    host = "localhost"
    port = 1337
    name = ""
    args = sys.argv[1:]
    if len(args) == 2 and args[0] in ["-l", "'--language'"] and args[1] in LANGUAGES.keys():
        lang = LANGUAGES[args[1]]
    else:
        locale.setlocale(locale.LC_ALL, "")
        lang = locale.getlocale(locale.LC_MESSAGES)[0] + '.UTF-8'
        if lang not in LOCALES:
            lang = "en_US.UTF-8"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        app = QApplication(sys.argv)

        window = LoginFormApp(s, lang)
        window.show()
        app.exec_()
        name = window.username

        if name == '':
            return

        client = Client(s)
        client.do_EOF()
        window = ChatApp(name, client, lang)

        rec = threading.Thread(target=recieve, args=(s, client, window))
        rec.daemon = True
        rec.start()

        window.show()

        # client.cmdloop()
        app.exec_()
