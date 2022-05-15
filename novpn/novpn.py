import sys
import subprocess
import signal

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
subprocess.run(base_cmd, shell=True)
