from updater import update
from vpn import start_vpn
import subprocess

"""
TODO:
    - Fix update holding back vpn start. Use threads and make threadsafe.
"""

if __name__ == "__main__":
    update()
    # Wait unitil vpncontrol is running
    subprocess.run(
        "bash -c 'until [[ $(pgrep -f vpncontrol) ]]; do sleep 1; done'", shell=True
    )
    start_vpn()
