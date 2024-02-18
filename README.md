**Status: Partly Maintained**

**Warning:** The owner of this repo has discontinued their NordVPN subscription. As a result, any changes introduced by NordVPN after 2023 may cause bugs or, in the worst case, make this software unusable.

The "partly maintained" status of this repo entails:

- The main branch is currently unmaintained.

- There is a second experimental branch in this repo that continues to receive updates and fixes.
  However, this branch is patched and only tested to use a different VPN provider. It strives to maintain backward compatibility with NordVPN but this is not verified.

# gui-nordvpn-linux description:

A gui for connecting to nordvpn servers on linux mint.
It uses openvpn for connecting to nordvpn servers. And gtk for python to create a system trayicon and gui.

Features:

- Autoconnect on boot
- Controlled by a trayicon
- Killswitch
- Split-tunnel

Preview trayicon:

![tray](https://github.com/insan271/gui-nordvpn-linux/blob/assets/.preview/tray.png)

![tray2](https://github.com/insan271/gui-nordvpn-linux/blob/assets/.preview/tray2.png)

Preview GUI:

![gui](https://github.com/insan271/gui-nordvpn-linux/blob/assets/.preview/gui.png)

# System requirements:

- Linux Mint (Also made it work on Raspberry PI OS. So it could work on everything debian/ubuntu based but this is not tested.)
- Systems installed python3 >= 3.7
- System uses systemd and can install packages with apt

# Don't install when:

- You use iptables for other applications. Stopping a vpn connection is currently programmed to flush all rules.

# Installation:

Follow these steps in a terminal.

Download :

**git clone https://github.com/insan271/gui-nordvpn-linux.git**

Optional switch to experimental branch:

**git checkout airvpn**

Give install.sh executable permission:

**cd gui-nordvpn-linux && chmod +x install.sh**

Run the install script:

**./install.sh**

Important use the Advanced configuration:Service credentials (manual setup)
found on https://my.nordaccount.com/dashboard/nordvpn/ in the install script. These are different from the regular username and password.

Once installed the credentials can't be changed.
So make sure these are correct or a uninstall and reinstall are needed.

If the install failed make sure to run the uninstall script for cleaning up.
Bug reports should contain the output from the install script.
or logs from **journalctl -u nvpn.service | tail -n 200*

# Uninstall:

Open a terminal in the location uninstall.sh is present.

Give it executable permission(**chmod +x uninstall.sh**).

Run the uninstall script(**./uninstall.sh**).

# Switching from experimental  to main branch:

A full uninstall is required.
After reinstall and replace from the install section **~~git checkout airvpn~~** with **git checkout main**

# Using the split-tunnel:

A split-tunnel allows to run an application outside the vpn connection.

To start an application in the splittunnel run this in a terminal:

**novpn cmd** where cmd is the command

Example:

**novpn firefox**

Or for desktop icons right click and select **Properties**
and add **novpn** in front of the **Command Field**

# Adding custom iptables or run extra scripts on vpn start/end :

After the vpn is started/ended it looks in the directory's  
 /etc/nvpn/postup (started) or /etc/nvpn/postdown (ended) for extra scripts to run.

This directory isn’t created by the program itself so it needs to be created manually:

**sudo mkdir -p /etc/nvpn/postup && sudo mkdir -p /etc/nvpn/postdown**

It only executes scripts with executable permissions so give the script permission with :

**sudo chmod +x
scriptName.sh**

# Note's for other developers that will read the code:

These scripts are 3 separate programs.
The vpn directory is the systemd service that controls the vpn.
The vpncontrol directory is the gui and trayicon that controls the vpn service with a unix socket.
The novpn directory contains scripts to start an application in the split-tunnel

<pre>
├── install.sh # The install script
├── installTools # Tools used by install.sh
│   ├── setupAutostart.py # Creates autostart on login
│   └── setupService.py # Creates the systemd service
├── LICENSE
├── novpn
│   ├── novpn.py # Starts process in split-tunel
│   └── novpn.sh # Linker to novpn.py that will be inserted in linux PATH env
├── README.md
├── uninstall.sh # Uninstall script
├── vpn # Systemd service runs as root 
│   ├── connectivity.py # A monitor that tests connectivity and reconnects when needed.
│   ├── main.py
│   ├── split_tunnel.py # Configures a split-tunnel network interface
│   ├── updater.py # Updates the nord ovpn files every 10 days
│   ├── uSocket.py # Unix socket for communication to vpncontrol(gui)
│   └── vpn.py # The code that handles the vpn and kill switch
└── vpncontrol
    ├── flags # Directory will hold images for the gui
    ├── helperFlaglist.py # Functions used by viewFlaglist.py gui. 
    ├── main.py
    ├── requirements.txt # Pip requirements for install.sh for creating a venv
    ├── uSocket.py # Unix socket for communication with vpn service
    ├── viewFlaglist.py # The gui where you can select a vpn server
    ├── viewTrayicon.py # The systems trayicon
    └── vpn.svg # Image used by trayicon
</pre>
