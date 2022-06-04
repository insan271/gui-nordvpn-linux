import signal
import subprocess, shlex, os, random, threading
import json
from typing import List
from uSocket import send_to_gui, start_Usocket
import logging
from split_tunnel import create_split_tunnel
from connectivity import _connectivity

"""

"""
logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(funcName)s:%(message)s / %(threadName)s",
    level=logging.INFO,
)

PATH_HOME = "/".join(
    os.path.abspath(__file__).split("/")[:3]
)  # Fixed, script runs as root so can't find users home with other methods.
PATH_VPN_FILES = os.path.join(os.path.dirname(__file__), "ovpn_tcp")

# Allows only one thread to run when 2 threads acquired the same semaphore.
# Stops racecondition between connectivity_monitor and vpn.reconnect|vpn.connect
semaphore = threading.BoundedSemaphore()


class _vpn(object):
    """
    Class that holds all actions to control/setup the vpn
    """

    def __init__(self):
        self.subp = []  # contains the openvpn process
        self.command = []  # openvpn command
        self.connected_last = ""
        self._vpn_files = self._get_vpn_files()
        self.active = False  # vpn is running or needs to run
        self.connectivity = _connectivity.start_connectivity_monitor(
            self, semaphore
        )  # returns setup class connectivity
        self.trys: int = 0  # Repeted connenction trys

    def connect(self, location: bytes):
        """External connect method for call by uSocket server"""
        with semaphore:  # block connectivity monitor until connection complete
            self._connect(location)

    def _connect(self, location: bytes, reconnect: bool = False):
        """
        (bytes, reconnect=bool) ->

        Starts connection to vpn.
        """
        logging.debug(f"{locals()}")
        logging.info(f"connecting try:{self.trys}")
        if reconnect:
            self._stop(clear_killswitch=False)
            if not self.active:  # iptables are reset:
                self.start_kill_switch(
                    self._get_vpn_file_ip(os.path.join(PATH_VPN_FILES, location))
                )

        else:
            self._stop(
                keep_internet_blocked=True
            )  # TODO add option clear kill switch block all trafic until new kill switch started
            location = self._get_random_ovpn(location.decode())  # vpn file as string

            # Start kill switch.
            self.start_kill_switch(
                self._get_vpn_file_ip(os.path.join(PATH_VPN_FILES, location))
            )

            self.command = shlex.split(
                f"openvpn --config {os.path.join(PATH_VPN_FILES, location)} --auth-user-pass /etc/openvpn/pass.txt"
            )

        # Start vpn.
        p = subprocess.Popen(self.command)
        logging.info("Started vpn subproccess")
        self.subp.append(p)
        self.connected_last = location

        # Connectivity check.
        if _connectivity.check_connection():
            self.active = True
            self.trys = 0
            _connectivity.connectivity_reset_timers()
            logging.info("connection complete")
            create_split_tunnel()
            logging.info("split tunnel available")
            send_to_gui(f"Connected to {location}")
            self._post_up_scripts()
            self.dedup_iptables()

        else:
            self.trys += 1
            if self.trys == 3:
                self.trys = 0
                self._check_auth()
                return
            # Parses also doubke vpn to correct location
            # Example: ch
            # nl-ch10.nordvpn.com.tcp
            # ch10.nordvpn.com.tcp
            self._connect(location.split("-")[-1][:2].encode())

    def auto_connect(self):
        """
        Connects to the most used vpn location if auto connect is enabled.
        """
        logging.info("called")
        sfile = os.path.join(PATH_HOME, ".nvpn", ".autoconnect")
        if os.path.exists(sfile):  # Autoconnect file exists.
            counter = os.path.join(PATH_HOME, ".nvpn", "counter.json")
            if os.path.exists(counter):  # Found file that counts most used location.
                with open(counter, "r") as f:
                    country = json.load(f)
                    most_used = sorted(country.items(), key=lambda x: -x[1])[0][0]
                    self.connect(
                        most_used.encode()
                    )  # Start connection to most used location.

    @staticmethod
    def start_kill_switch(vpn_ip: str):
        """
        (str) ->

        Takes ip address and starts kill switch.
        """
        logging.info("called")
        local_net = subprocess.check_output(
            "ip route | awk '/default/ { print $3 }' | sed 's/.$/0\/24/g'", shell=True
        ).decode()
        rules = [
            "iptables -P OUTPUT DROP",
            "iptables -A OUTPUT -o lo -j ACCEPT",
            f"iptables -A OUTPUT -d {local_net} -j ACCEPT",
            f"iptables -A OUTPUT -d {vpn_ip} -j ACCEPT",
            "iptables -A OUTPUT -o tun+ -j ACCEPT",
        ]

        for x in rules:
            subprocess.run(shlex.split(x))
        logging.info("kill switch ON")

    @staticmethod
    def stop_kill_switch(keep_internet_blocked=False):
        """
        Flushes kill swith.
        """
        logging.info("called")
        rules = [
            "iptables -F",
            "iptables -P OUTPUT ACCEPT",
        ]
        if keep_internet_blocked:
            rules.pop()
            rules.append("iptables -P OUTPUT DROP")

        for x in rules:
            subprocess.run(shlex.split(x))

    def _stop(self, clear_killswitch: bool = True, keep_internet_blocked=False):
        """
        Command that handles stopping a vpn connection internal.
        """
        logging.debug("called")
        if self.subp:
            for x in self.subp:
                # x.terminate()
                logging.info("send SIGINT to vpn subproccess and waiting to stop")
                x.send_signal(signal.SIGINT)
                x.wait()
                logging.info("stopped vpn subproccess.")
            self.subp = []
            send_to_gui("Stopped")
        if clear_killswitch:
            self.stop_kill_switch(keep_internet_blocked=keep_internet_blocked)
        self._post_down_scripts()

    def stop(self):
        """
        Command that handles stopping a vpn connection external.
        """
        with semaphore:
            logging.info("called")
            self.active = False
            self._stop()

    def reconnect(self):
        """
        Reconnect to stopped vpn.
        """
        with semaphore:  # wait until connectivity_monitor task is done and block it until vpn is connected
            logging.info("called")
            if self.command and self.connected_last:
                self._connect(self.connected_last, reconnect=True)

    def _check_auth(self):
        """
        Run when connecting 5 times in a row failed.
        Send bad auth message
        """
        logging.info("Connecting failed  5 times. Testing possible problem")
        # Test internet.
        # Internet blocked by iptables so testing in splittunnel.
        create_split_tunnel()
        ping = subprocess.run(
            "novpn timeout 3 ping -c 1 google.com", shell=True, capture_output=True
        ).stdout.decode()
        if "1 received" in ping:
            # Internet detected but connecting to vpn failed
            # Send bad auth to gui
            self.stop()
            send_to_gui("AUTH Failed")
            logging.error("Connection failed: possible bad auth.")
        else:
            logging.info("Connection failed and pauzed retry: no internet detected")

    def _get_random_ovpn(self, location: str) -> str:
        """
        (str) -> str

        Return a random ovpn file for input location.
        """
        # temp = [x for x in self._vpn_files if location in x.split(".")[0]]
        temp = [x for x in self._vpn_files if location in x.split("-")[-1][:2]]
        assert temp, "Expected to find vpn files"
        return random.choice(temp)

    @staticmethod
    def _get_vpn_files() -> List[str]:
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
        logging.info(os.path.join(file_vpn))
        return (
            subprocess.run(
                f"grep -v '^#' {file_vpn} | grep -v '^$' | grep remote\  | awk '{{print $2}}' | head -n 1",
                shell=True,
                capture_output=True,
            )
            .stdout.decode()
            .split()[0]
        )

    @staticmethod
    def _post_up_scripts():
        """
        Executes all scripts when vpn connection
        is up and running in : /etc/nvpn/postup/*
        Can be used to enable custom iptables.
        """
        path = "/etc/nvpn/postup/"
        if os.path.exists(path):
            files = (
                x
                for x in os.listdir(path)
                if os.path.isfile(path + x) and os.access(path + x, os.X_OK)
            )
            for x in files:
                subprocess.run(path + x, shell=True)

    @staticmethod
    def _post_down_scripts():
        """
        Executes all scripts when vpn connection
        is closed : /etc/nvpn/postup/*
        Can be used to remove custom rules.
        """
        path = "/etc/nvpn/postdown/"
        if os.path.exists(path):
            files = (
                x
                for x in os.listdir(path)
                if os.path.isfile(path + x) and os.access(path + x, os.X_OK)
            )
            for x in files:
                subprocess.run(path + x, shell=True)

    @staticmethod
    def dedup_iptables():
        """
        Removes duplicate iptables
        """
        subprocess.run(
            "iptables-save | awk '/^COMMIT$/ { delete x; }; !x[$0]++' | sudo iptables-restore",
            shell=True,
        )


def start_vpn():
    """
    Start's the unix socket that will control the vpn
    """
    vpn = _vpn()
    start_Usocket(vpn)


if __name__ == "__main__":
    start_vpn()
