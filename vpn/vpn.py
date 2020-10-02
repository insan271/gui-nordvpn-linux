import subprocess, shlex, os, random
import time, json
from uSocket import send_to_gui, start_Usocket

PATH_HOME = "/".join(
    os.path.abspath(__file__).split("/")[:3]
)  # Fixed, script runs as root so can't find users home with other methods.
PATH_VPN_FILES = os.path.join(os.path.dirname(__file__), "ovpn_tcp")


def start_vpn():
    """
    Start's the unix socket that will control the vpn
    """
    vpn = _vpn()
    start_Usocket(vpn)


class _vpn(object):
    """
    Class that holds all actions to control/setup the vpn
    """
    def __init__(self):
        self.subp = []
        self.command = []
        self.connected_last = ""
        self._vpn_files = self._get_vpn_files()
        self._auto_connect()

    def connect(self, location, reconnect=False):
        """
        (bytes, reconnect=bool) ->

        Starts connection to vpn.
        """
        if reconnect:
            self.stop()
        else:
            self.stop()
            location = self._get_random_ovpn(
                location.decode()
            )  # Variable needed for creation command and kill switch.
            self.command = shlex.split(
                f"openvpn --config {os.path.join(PATH_VPN_FILES, location)} --auth-user-pass /etc/openvpn/pass.txt"
            )
        # Start kill switch.
        self.start_kill_switch(
            self._get_vpn_file_ip(os.path.join(PATH_VPN_FILES, location))
        )

        # Start vpn.
        p = subprocess.Popen(self.command)
        self.subp.append(p)
        self.connected_last = location

        # Connectivity check.
        if self.check_connection():
            send_to_gui(f"Connected to {location}")
        else:
            self.connect(location[:2].encode()) 

    def _auto_connect(self):
        """
        Connects to the most used vpn location if auto connect is enabled.
        """
        sfile = os.path.join(PATH_HOME, ".nvpn", ".autoconnect")
        if os.path.exists(sfile):  # Autoconnect file exists.
            counter = os.path.join(PATH_HOME, ".nvpn", "counter.json")
            if os.path.exists(counter):  # Found file that counts most used location.
                with open(counter, "r") as f:
                    country = json.load(f)
                    most_used = sorted(country.items(), key=lambda x: -x[1])[0][0]
                    self.connect(most_used.encode()) # Start connection to most used location. 

    @staticmethod
    def check_connection():
        """
        () -> bool
        Check if vpn is active.
        Ping and check for internet connectivity.
        """
        for _ in range(6):
            # Check vpn up.
            result = subprocess.run(
                "cat /proc/net/dev | grep tun | head -n 1",
                shell=True,
                capture_output=True,
            ).stdout.decode()

            # Ping to test internet.
            if "tun" in result:
                ping = subprocess.run(
                    "ping -c 1 startpage.com", shell=True, capture_output=True
                ).stdout.decode()
                if "1 received" in ping:
                    return True
            time.sleep(1)
        return False

    @staticmethod
    def start_kill_switch(vpn_ip):
        """
        (str) ->

        Takes ip address and starts kill switch.
        """
        rules = [
            "iptables -P OUTPUT DROP",
            "iptables -A OUTPUT -o lo -j ACCEPT",
            "iptables -A OUTPUT -d 192.168.1.0/24 -j ACCEPT",
            f"iptables -A OUTPUT -d {vpn_ip} -j ACCEPT",
            "iptables -A OUTPUT -o tun+ -j ACCEPT",
        ]

        for x in rules:
            subprocess.run(shlex.split(x))

    @staticmethod
    def stop_kill_switch():
        """
        Flushes kill swith.
        """
        rules = [
            "iptables -F",
            "iptables -P OUTPUT ACCEPT",
        ]

        for x in rules:
            subprocess.run(shlex.split(x))

    def stop(self):
        """
        Command that handles stopping a vpn connection.
        """
        if self.subp:
            for x in self.subp:
                x.terminate()
            self.subp = []
            send_to_gui("Stopped")
        self.stop_kill_switch()

    def reconnect(self):
        """
        Reconnect to stopped vpn.
        """
        if self.command and self.connected_last:
            self.connect(self.connected_last, reconnect=True)

    def _get_random_ovpn(self, location):
        """
        (str) -> str

        Return a random ovpn file for input location.
        """
        temp = [x for x in self._vpn_files if location in x.split(".")[0]]
        assert temp, "Expected to find vpn files"
        return random.choice(temp)

    @staticmethod
    def _get_vpn_files():
        """
        () -> [str]

        Return list of available ovpn files.
        """
        return [
            x
            for x in os.listdir(PATH_VPN_FILES)
            if os.path.isfile(os.path.join(PATH_VPN_FILES, x))
        ]

    @staticmethod
    def _get_vpn_file_ip(file_vpn):
        """
        (str) -> str

        Returns the server ip for inputted vpn file.
        """
        return (
            subprocess.run(
                f"grep -v '^#' {os.path.join(PATH_VPN_FILES, file_vpn)} | grep -v '^$' | grep remote\  | awk '{{print $2}}' | head -n 1",
                shell=True,
                capture_output=True,
            )
            .stdout.decode()
            .split()[0]
        )