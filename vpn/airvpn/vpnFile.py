import os, logging, json, random
from airvpn import updater
from pathlib import Path

PATH = Path(__file__).parents[1]
JSON = os.path.join(PATH, 'airvpn.json')

def get_airvpn_ovpn(location: str) -> str:
    """
    (str) -> str

    Return a random ovpn location for input location.
    """
    # temp = [x for x in self._vpn_files if location in x.split(".")[0]]
    updater.force_update()
    with open(JSON, "r") as f:
        data = json.load(f)
    server_list = [
        x for x in data['servers'] if x["country_code"]== location and x['health'] == "ok"
    ]
    server = {}
    count = 0
    while "ip_v4_in3" not in server and count <= 10:
        server = random.choice(server_list)
        count += 1
    if count >= 10: assert("Fatal error in get_airvpn_ovpn: cant find a server")
    return _generate_vpn_file(server["ip_v4_in3"], location)

def _generate_vpn_file(ip, location):
    with open(os.path.join(PATH, "client.crt"), "r") as f:
        cert = f.read().rstrip()

    with open(os.path.join(PATH, "client.key"), "r") as f:
        key = f.read().rstrip() 

    template= f"""client
dev tun
remote {ip} 443
resolv-retry infinite
nobind
persist-key
persist-tun
auth-nocache
verb 3
explicit-exit-notify 5
push-peer-info
setenv UV_IPV6 yes
remote-cert-tls server
comp-lzo no
data-ciphers AES-256-GCM:AES-256-CBC:AES-192-GCM:AES-192-CBC:AES-128-GCM:AES-128-CBC
data-ciphers-fallback AES-256-CBC
proto udp
auth SHA512
script-security 2
up /etc/openvpn/update-resolv-conf
down /etc/openvpn/update-resolv-conf
<ca>
-----BEGIN CERTIFICATE-----
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
-----END CERTIFICATE-----
</ca>
<cert>
{cert}
</cert>
<key>
{key}
</key>
<tls-crypt>
-----BEGIN OpenVPN Static key V1-----
a3a7d8f4e778d279d9076a8d47a9aa0c
6054aed5752ddefa5efac1ea982740f1
ffcabadf0d3709dae18c1fad61e14f72
a8eb7cb931ed0209e67c1d325353a657
a1198ef649f1c23861a2a19f2c6b27aa
5e43be761e0c71e9c2e8d33b75af289e
ffb1b1e4ec603d865f74e2b4348ff631
c5c81202d90003ed263dca4022aa9861
520e00cc26e40fa171b9985a2763ccb4
c63560b7e6b0f897978fb25a2d5889cd
6d46a29509fa09830aff18d6e81a8dc1
a0182402e3039c3316180e618705ca35
f2763f8a62ca5983d145faa2276532ae
5e18459a0b729dc67f41b928e592b394
67ec3d79c70205595718b1bce56ca4ff
58e692ce09c8282d2770d2bf5c217c06
-----END OpenVPN Static key V1-----
</tls-crypt>
    """
    vpn_file = os.path.join(PATH, f"{location}.ovpn")
    with open(vpn_file, "w") as f:
        f.write(template)
    return vpn_file    