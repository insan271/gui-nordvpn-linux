import os

PATH_MAIN = os.path.join(os.path.expanduser("~"), ".nvpn", "vpn", "main.py")

print(
    f"""[Unit]
Description=Openvpn wrappper for nordvpn
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
ExecStart=python3 {PATH_MAIN}

[Install]
WantedBy=multi-user.target
"""
)
