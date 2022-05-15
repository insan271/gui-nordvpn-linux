import socket
from threading import Thread
import signal

_SOCK = ""  # Variable that will hold the socket server


def send(message):
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


def start_reciever(notifyer, tooltip):
    """
    (Notify.Notification(), Gtk.StatusIcon.set_tooltip_text()) ->

    Starts a unix socket server for receiving messages from vpn scripts.
    """

    def usock(notifyer, tooltip):
        server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        server.bind("\0trayiconvpn")
        global _SOCK
        _SOCK = server
        while 1:
            data, _ = server.recvfrom(64)
            if "Connected" in data.decode():
                notifyer("Command", data.decode()).show()
                tooltip(data.decode())

            elif "AUTH Failed" in data.decode():
                notifyer("AUTH FAILED", "Uninstall and reinstall nvpn required").show()
                tooltip("BAD AUTH: please reinstall nvpn with correct credentials")
            elif "Stopped" in data.decode():
                tooltip("No vpn connection")

    signal.signal(signal.SIGINT, stop_receiver)  # Capture sigint for closing the server
    Thread(
        target=usock,
        args=(
            notifyer,
            tooltip,
        ),
        daemon=True,
    ).start()


def stop_receiver():
    """
    Closes gui's socket server
    """
    _SOCK.close()
