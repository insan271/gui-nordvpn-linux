import subprocess, shlex
import uSocket


def _NS_exists() -> bool:
    """Checks if network namespace exists"""
    output = subprocess.run(
        "ip netns list", shell=True, capture_output=True
    ).stdout.decode()
    return "novpn" in output


def create_split_tunnel():
    """Create network namespace where internet is accessed outside the vpn"""
    if _NS_exists():
        stop_split_tunnel()

    IFACE_INTERNET = (
        subprocess.check_output("route | awk '/default/ { print $NF }'", shell=True)
        .decode()
        .strip()
    )
    IFACE_NS = ""
    IFACE_NOVPN = ""
    GETAWAY = (
        subprocess.check_output("ip route | awk '/default/ { print $3 }'", shell=True)
        .decode()
        .strip()
    )
    DNS = GETAWAY

    rules = [
        "ip netns add novpn",
        "ip link add novpn0 type veth peer name v-eth0 netns novpn",
        "ip addr add 10.18.1.1/24 dev novpn0",
        "ip link set dev novpn0 up",
        "ip netns exec novpn ip -n novpn addr add 10.18.1.2/24 dev v-eth0",
        "ip netns exec novpn ip link set v-eth0 up",
        "ip netns exec novpn ip link set dev lo up",
        "ip netns exec novpn ip route add default via 10.18.1.1 dev v-eth0",
        "sysctl -w net.ipv4.ip_forward=1",
        f"iptables -t nat -A POSTROUTING -s 10.18.1.2/24 -o {IFACE_INTERNET} -j MASQUERADE",
        f"iptables -A FORWARD -i {IFACE_INTERNET} -o novpn0 -j ACCEPT",
        f"iptables -A FORWARD -o {IFACE_INTERNET} -i novpn0 -j ACCEPT",
        f'mkdir -p /etc/netns/novpn && echo "nameserver {DNS}" > /etc/netns/novpn/resolv.conf',
        f"ip route add table 100 default via {GETAWAY}",
        "ip rule add fwmark 345345 table 100",
        "iptables -t mangle -A PREROUTING -i novpn0 -j MARK --set-mark 345345",
    ]

    for x in rules:
        subprocess.run(x, shell=True)


def stop_split_tunnel():
    rules = [
        "ip li delete novpn0",
        "ip netns del novpn",
        "rm -fr /etc/netns/novpn",
        "ip route flush table 100",
    ]
    for x in rules:
        subprocess.run(shlex.split(x))


def run_in_split_tunnel(cmd: str):
    user = (
        subprocess.run(
            "who -u | awk '{ print $1 }' | head -n  1  ",
            shell=True,
            capture_output=True,
        )
        .stdout.decode()
        .strip()
    )
    pre = f"ip netns exec novpn runuser -u {user} "
    uSocket.send_to_gui(f"Connected:\n{cmd}\noutside vpn \nas {user}")

    subprocess.Popen(shlex.split(pre + cmd))
