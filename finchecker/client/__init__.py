"""Init file with all functionality for client."""

import socket
import sys
import cmd
import threading

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QFormLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt


class Client(cmd.Cmd):
    """Class for sending requests to server with ability of using cmd instead of GUI."""

    prompt = ":->"

    uid = 0
    file_name = dict()

    def __init__(self, conn, stdin=sys.stdin):
        """
        Initialize variables.

        :param conn: socket to server
        :param stdin: input stream
        """
        super().__init__(stdin=stdin)

        self.conn = conn

    def do_req(self, cmd, filename, args=''):
        """
        Send request to server.

        :param cmd: type of command
        :param filename: name of file where it will be stored
        :param args: arguments for executing command
        """
        Client.file_name[Client.uid] = filename
        Client.uid = (Client.uid + 1) % 1000
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
        self.conn.sendall(("sayall " + msg + "\n").encode())

    def do_EOF(self, args):
        """End client activity."""
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
