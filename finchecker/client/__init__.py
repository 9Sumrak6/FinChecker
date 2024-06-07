import socket
import sys
import cmd

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

        print(f"\n{data.strip()}\n{cmd.prompt}{readline.get_line_buffer()}", end='', flush=True)

def main():
    """Start client."""
    host = "localhost"
    port = 1337
    name = "me"

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