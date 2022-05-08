import signal, socket, sys
from split_tunnel import run_in_split_tunnel


def start_Usocket(vpn):
    """
    (_vpn) ->

    Starts a socket server.
    Socket server is used for accepting controls from gui script.
    """
    server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    server.bind("\0vpn")

    # Stop called by sigint.
    def end(sig, frame):
        print("sig end")
        nonlocal server
        server.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, end)

    while 1:
        data, _ = server.recvfrom(128)
        if (not data) or data == b"end":
            break
        else:
            temp = data.split()  # Bytes list.

            # Received commands/actions.
            commands = {
                b"connect": lambda: vpn.connect(temp[1]),
                b"stop": lambda: vpn.stop(),
                b"reconnect": lambda: vpn.reconnect(),
                b"split": lambda: run_in_split_tunnel(temp[1].decode()),
            }
            if temp[0] in commands:  # Check if received command exists.
                commands[temp[0]]()

    server.close()


def send_to_gui(message):
    """
    (str) ->

    Sends message to the gui script socket server.
    """
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        client.connect("\0trayiconvpn")
        client.send(message.encode())
    except:
        pass


def send_to_self(message):
    """
    (str) ->
    Send a message the unix socket server that controls the vpn.
    """
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        client.connect("\0vpn")
        client.send(message.encode())
        client.close()
    except:
        pass
