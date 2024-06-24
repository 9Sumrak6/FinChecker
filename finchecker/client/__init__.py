import socket
import sys
import cmd
import threading


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

def recieve(conn, client):
    """Recieve the messages from server in another thread."""
    files = dict()

    while conn is not None:
        data = ""

        new = conn.recv(1024)
        cmd = new[:5].decode()

        if cmd == 'begin' or cmd[:3] == 'end':
            pass
        else:
            pass

        # print(f"\n{data.strip()}\n{cmd.prompt}{readline.get_line_buffer()}", end='', flush=True)


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

        client = Client(s)

        rec = threading.Thread(target=recieve, args=(s, client))
        rec.daemon = True
        rec.start()

        client.cmdloop()