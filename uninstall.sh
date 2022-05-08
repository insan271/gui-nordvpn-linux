# Checking run as user.
if [ $(whoami) != "root" ]; then
    echo "Uninstall running as user. Ok."
else
    echo "Uninstall script needs to run as user. FAILED to uninstall. running as root  "
    exit 1
fi

echo "Needs sudo permission for uninstalling root owned files"

sudo systemctl stop nvpn.service
sudo systemctl disable nvpn.service
pkill -f vpncontrol/main.py
sudo pkill -f openvpn

# Flushing kill switch.
sudo iptables -F 
sudo iptables -P OUTPUT ACCEPT

sudo rm /usr/local/bin/novpn
sudo rm -r $HOME/.nvpn
sudo rm -f /etc/systemd/system/nvpn.service
sudo rm -f /etc/openvpn/pass.txt
rm -f $HOME/.config/autostart/vpncontrol.desktop

