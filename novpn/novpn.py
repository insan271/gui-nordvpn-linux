import sys
import subprocess
import signal
import socket

"""
novpn cmd
Example: novpn firefox

Starts a process in the split tunnel
"""

user = (
    subprocess.run(
        "who -u | awk '{ print $1 }' | head -n  1  ",
        shell=True,
        capture_output=True,
    )
    .stdout.decode()
    .strip()
)

# Exit without error code
signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))

cmd = " ".join(sys.argv[1:])
base_cmd = f'sudo ip netns exec novpn runuser {user} -c "{cmd}"'

client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
client.connect("\0trayiconvpn")
client.send(f"Starting {cmd} in splittunnel".encode())
client.close()

subprocess.run(base_cmd, shell=True)
