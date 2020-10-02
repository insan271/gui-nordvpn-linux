from updater import update
from vpn import start_vpn

"""
TODO:
    - Fix update holding back vpn start. Use threads and make threadsafe.
"""

if __name__ == "__main__":
    update()
    start_vpn()
