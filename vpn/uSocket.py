import signal, socket, sys, time, logging, threading


def start_Usocket(vpn):
    """
    (_vpn) ->

    Starts a socket server.
    Socket server is used for accepting controls from gui script.
    """
    # Start vpn if autoconnect is enabled
    threading.Thread(target=vpn.auto_connect, args=(), daemon=True).start()

    server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    server.bind("\0vpn")

    # Stop called by sigint.
    def end(sig, frame):
        print("sig end")
        vpn.stop()
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
                b"connect": lambda: threading.Thread(
                    target=vpn.connect, args=(temp[1],), daemon=True
                ).start(),
                b"stop": lambda: threading.Thread(
                    target=vpn.stop, args=(), daemon=True
                ).start(),
                b"reconnect": lambda: threading.Thread(
                    target=vpn.reconnect, args=(), daemon=True
                ).start(),
                b"status": lambda: received(),
            }
            if temp[0] in commands:  # Check if received command exists.
                commands[temp[0]]()

    server.close()


def received():
    """
    Status code result in response to end_to_gui
    """
    logging.info("STATUS 200")
    send_to_gui.__dict__.update({"received": True})


def send_to_gui(message: str):
    """
    (str) ->

    Sends message to the gui script socket server.
    """
    timeout = 0
    limit = 60
    send_to_gui.received = False
    while not send_to_gui.received and timeout < limit:
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            client.connect("\0trayiconvpn")
            client.send(message.encode())
            logging.info("Send data complete")
        except:
            pass
        time.sleep(0.5)
        timeout += 1
    if timeout >= limit:
        logging.error(f"msg: {message}. send to gui Failed")


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
