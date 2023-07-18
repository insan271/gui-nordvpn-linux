from updater import update
from vpn import start_vpn
import subprocess
import os
from airvpn import updater

"""
TODO:
    - Fix update holding back vpn start. Use threads and make threadsafe.
"""

PATH_HOME = "/".join(
    os.path.abspath(__file__).split("/")[:3]
) 
PATH_AIRFLAG = os.path.join(PATH_HOME, ".nvpn", ".airvpn")
mode = "airvpn" if os.path.exists(PATH_AIRFLAG) else "nordvpn"


if __name__ == "__main__":
    if mode != "airvpn":
        update()
    else:
        updater.force_update()
    # Wait unitil vpncontrol is running
    subprocess.run(
        "bash -c 'until [[ $(pgrep -f vpncontrol) ]]; do sleep 1; done'", shell=True
    )
    start_vpn(mode)
