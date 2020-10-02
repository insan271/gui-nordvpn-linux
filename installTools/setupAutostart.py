import os

PATH_VENV = os.path.join(
    os.path.expanduser("~"), ".nvpn", "vpncontrol", "venv", "bin", "python3"
)
PATH_TRAY = os.path.join(os.path.expanduser("~"), ".nvpn", "vpncontrol", "main.py")

print(
    f"""[Desktop Entry]
Type=Application
Exec={PATH_VENV} {PATH_TRAY}
X-GNOME-Autostart-enabled=true
NoDisplay=false
Hidden=false
Name=vpncontrol
Comment=VPN controlller for nordvpn
X-GNOME-Autostart-Delay=0
"""
)
