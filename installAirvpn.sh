if ! test -f "client.cert" && ! test -f "client.key" ; then
    echo "Can't install client for airvpn. Can't find client.cert and client.key in directory"
    exit 1
fi

echo "Installing vpn client for nordvpn in $HOME/.nvpn"

# Checking install is run as user.
if [ $(whoami) != "root" ]; then
    echo "Install running as user. Ok."
else
    echo "Install script needs to run as user. FAILED to uninstall. running as root  "
    exit 1
fi

echo "Checking if system is supported:"

# Checking if apt and systemd are installed.
case $(which apt && which systemd && echo "ok") in
    *ok*)
        echo "Apt and systemd check. OK.";;
        
    *)
        echo "Failed to install. Only works on linux with apt as package manager and systemd installed"
        exit 1;
esac

# Checking for internet
wget -q --spider http://google.com
if [ $? -eq 0 ]; then
    echo "Connected to internet: OK"
else
    echo "Failed to install. No internet detected."
    exit 1
    
fi

# Checking if bc is installed BUG FIX rpi4.
case $(which bc) in
    *bin*)
        echo "";;
        
    *)
        sudo apt install bc
esac

# Checking if correct python version is installed
pyvf=$(python3 --version | sed 's/[^0-9.]*//g' | head -c4 | sed 's/\.$//')
pyvMain=$(echo "$pyvf" | head -c1  )
pyvSub=$(echo "$pyvf" | cut -d "." -f 2 )
if [ "$pyvMain" -eq 3 ] && [ "$pyvSub" -ge 6 ] ; then
    echo "Python version is ok."
else
    echo "Can't install on this systen. Needs python version >= 3.6"
    exit 1
fi


# Checking if kill switch is supported. Router ip range needs to be 192.168.1.* else system not supported
case $(sudo route | grep "192.168.1.0" | head -n 1) in
    *"192.168.1.0"*)
        echo "Killswitch support. OK.";;
        
    *)
        echo "Failed to install. System not supported. Router ip range other than 192.168.1.* gives problem with killswitch"
        exit 1;
esac


# Installing needed dependencies
echo "Installing needed apt dependencies: "

case $(sudo apt list --installed | grep openresolv) in 
  *"openresolv"*)
        ;;
  *) 
    sudo apt install resolvconf
esac

sudo apt install iptables openvpn openvpn-systemd-resolved libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0 python3-venv gir1.2-appindicator3-0.1

# Creating installation path
basePATH="$( cd "$( dirname "$BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)"
mkdir -p $HOME/.nvpn 
sudo cp -r $basePATH/vpn $HOME/.nvpn 
sudo chown -R root $HOME/.nvpn/vpn # Makes root owner. 
sudo chmod -R 700  $HOME/.nvpn/vpn  # Vpn needs root permission. User is not allowed to edit files(security risk)
cp -r $basePATH/vpncontrol $HOME/.nvpn

# Setting up for airvpn
sudo cp client.crt $HOME/.nvpn/vpn/
sudo cp client.key $HOME/.nvpn/vpn/
touch $HOME/.nvpn/.airvpn
touch $HOME/.nvpn/vpncontrol/.airvpn

# Creating python venv and installing dependencies for vpncontrol
python3 -m venv $HOME/.nvpn/vpncontrol/venv
echo "Installing created python venv dependencies with pip:"
$HOME/.nvpn/vpncontrol/venv/bin/pip install -r $HOME/.nvpn/vpncontrol/requirements.txt

# Creating auto startup when user logs in.
python3 $basePATH/installTools/setupAutostart.py > $HOME/.config/autostart/vpncontrol.desktop
 
# Downloading images for vpncontroller gui
mkdir -p $HOME/.nvpn/vpncontrol/flags
cd $HOME/.nvpn/vpncontrol/flags
echo "Downloading images needed for gui."
curl -O https://flagcdn.com/128x96.zip
unzip 128x96.zip
mv gb.png uk.png # Rename file so it is correct name for vpn gui script

# Creating novpn for running commands in split tunnel
#sudo (echo "#\!$(which python3)" && cat $basePATH/novpn/novpn.py)> /usr/local/bin/novpn
(echo "#!$(which python3)"&& cat $basePATH/novpn/novpn.py) > temp
sudo mv temp /usr/local/bin/novpn
sudo chmod +x /usr/local/bin/novpn

# Creating systemd service
serviceText="$(python3 ${basePATH}/installTools/setupService.py)"
sudo sh -c "echo '${serviceText}' > /etc/systemd/system/nvpn.service"
sudo systemctl enable nvpn.service
sudo systemctl daemon-reload
sudo systemctl start nvpn.service 

# Creating novpn for accessing split tunnel
sudo mkdir -p /usr/local/lib/novpn
sudo cp $basePATH/novpn/novpn.py /usr/local/lib/novpn/
sudo sed -i "1 i \#\!$(which python3)" /usr/local/lib/novpn/novpn.py
sudo cp $basePATH/novpn/novpn.sh /usr/local/bin/novpn
sudo chmod +x /usr/local/bin/novpn
sudo chmod 750 /usr/local/lib/novpn/novpn.py
# Making novpn accessible for none sudo users 
sudo su -c 'echo "ALL ALL = NOPASSWD:/usr/local/lib/novpn/novpn.py" > /etc/sudoers.d/novpn'
sudo chmod 440 /etc/sudoers.d/novpn

# Waiting for ovpn files installed and ready
echo "Waiting for ovpn files installed and ready."
x=1 # Counter bug fix rpi4. rpi never shows "Update vpn files complete."
while [ $x -le 40 ]:
do
    ovpnFilesOk=$(sudo systemctl status nvpn.service | grep "Update vpn files complete." | head -n 1)
    case $ovpnFilesOk in
        *"Update vpn files complete."*)
            break;;
        *) 
            sleep 1
            x=$(( $x + 1 ));;
    esac

done

echo "Starting trayicon."

# Fix script started in SSH
case $(pstree -ps $$) in

  *"ssh"*)
   (export DISPLAY=:0 &&  $HOME/.nvpn/vpncontrol/venv/bin/python3 $HOME/.nvpn/vpncontrol/main.py &>/dev/null) &
    ;;
  *) 
  ($HOME/.nvpn/vpncontrol/venv/bin/python3 $HOME/.nvpn/vpncontrol/main.py &>/dev/null) &
esac


