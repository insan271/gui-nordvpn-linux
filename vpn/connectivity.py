import logging, time, subprocess, threading
from uSocket import send_to_self


class Timer:
    def __init__(self):
        self.now = int(time.time())

    @property
    def last_call(self):
        temp = self.now
        self.now = int(time.time())
        value = int(time.time()) - temp
        logging.debug(value)
        return value


class _connectivity:
    """
    Part connectivity for the vpn class.
    Needs to be called with _connectivity.start_connectivity_monitor(vpn)
    in class vpn
    """

    _timer_counts: int = Timer()
    _timer_i_up: int = Timer()  # Network interface up
    _timer_ping: int = Timer()  # last ping
    _counter: int = 0
    _vpn = None
    semaphore = None

    @classmethod
    def connectivity_reset_timers(cls):
        """
        Stops connectiviy_monitor temporarily from regesitering
        all network evennts

        """
        # Reset timers
        cls._timer_i_up.last_call
        cls._timer_counts.last_call

    @classmethod
    def start_connectivity_monitor(cls, vpn, semaphore):
        """
        Setup connectivity class,
        starts a connectivity monitor
        and returns cls connectivity
        """
        logging.info("called")
        cls._vpn = vpn

        # Stops race condition
        # To block vpn when connetivity monitor is in the semaphore.
        cls.semaphore = semaphore

        x = threading.Thread(target=cls._connectivity_monitor, args=(), daemon=True)
        x.start()
        return cls

    @classmethod
    def _connectivity_monitor(cls):
        """
        A daemon that monitors network interface events.
        and preforms connectivity checks.
        """
        with subprocess.Popen(["ip", "monitor"], stdout=subprocess.PIPE) as proc:
            while True:
                data: str = proc.stdout.read1().decode().lower()
                with cls.semaphore:  # block when vpn is connecting
                    if cls._vpn.active:
                        # >3 seconds need to be past after last data received
                        # or timer started before checking if a connectify
                        # check is needed.
                        logging.debug("Data event")
                        # Interface up detected
                        if "state up" in data and cls._timer_i_up.last_call > 3:
                            if not cls.check_connection(trys=1):
                                logging.info(
                                    " Detected interface up no internet. Send reconnect"
                                )
                                send_to_self("reconnect")
                            continue

                        if cls._timer_counts.last_call > 3:
                            cls._counter += 1
                            # Random connectifty check every 6 data received events
                            if cls._counter % 10 == 0:
                                if not cls.check_connection(trys=1):
                                    logging.info(
                                        " Network monitor detected no internet. Send reconnect"
                                    )
                                    send_to_self("reconnect")

    @classmethod
    def check_connection(cls, trys: int = 6) -> bool:
        """
        Check if vpn is active.
        Ping and check for internet connectivity.
        Returns True on connection success
        """
        return_val = False
        logging.info(f"Checking connectifty. try:{trys}")
        for _ in range(trys):
            # Check vpn up.
            result = subprocess.run(
                "cat /proc/net/dev | grep tun | head -n 1",
                shell=True,
                capture_output=True,
            ).stdout.decode()

            # Ping to test internet.
            if "tun" in result:
                ping = subprocess.run(
                    "timeout 3 ping -c 1 startpage.com", shell=True, capture_output=True
                ).stdout.decode()
                if "1 received" in ping:
                    logging.info("Connectivity ping success")
                    return True
                    # return_val = True
                    # break
            time.sleep(1)
        cls.connectivity_reset_timers()

        # If failed try ping google as fall back

        if not return_val and "tun" in result:
            out = subprocess.run(
                "timeout 3 ping -c 1 google.com", shell=True, capture_output=True
            ).stdout.decode()
            logging.info("Connectivity ping failed. trying ping google instead")
            if "1 received" in out:
                logging.info("Connectivity ping google success")
                return True
            return False
        return False
