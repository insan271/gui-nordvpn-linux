# gui-nordvpn-linux description:
A gui for connecting to nordvpn servers on linux mint.
It uses openvpn for connecting to nordvpn servers. And gtk for python to create a system trayicon and gui.

Features:
- Autoconnect on boot
- Controlled by a trayicon
- Killswitch

Preview trayicon:
![tray](https://github.com/insan271/gui-nordvpn-linux/blob/assets/.preview/tray.png)
![tray2](https://github.com/insan271/gui-nordvpn-linux/blob/assets/.preview/tray2.png)


Preview GUI:
![gui](https://github.com/insan271/gui-nordvpn-linux/blob/assets/.preview/gui.png)

# System requirements:
- Linux Mint (Also made it work on Raspberry PI OS. So it could work on everything debian/ubuntu based but is not tested.)
- Systems installed python3 >= 3.6
- System uses systemd and can install packages with apt
- Router ip range is in 192.168.1.* (Killswitch assumes this)

# Don't install when:
- You use iptables for other applications. Stopping a vpn conection is currently programmed to flush all rules.
- Multiple users are on your linux installation. The trayicon only shows for the user that installed it. The systemd service starts for every user login.

# Installation:
Download in terminal(**git clone https://github.com/insan271/gui-nordvpn-linux.git**).
In terminal give install.sh executable permision(**cd gui-nordvpn-linux && chmod +x install.sh**).
Run the install script(**./install.sh**).
If the install failed make sure to run the uninstall script for cleaning up.
Bug reports should contain the ouput from the install script and the output of sudo systemctl status nvpn.service.

# Uninstall:
Open a terminal in the location uninstall.sh is present.
Give it executable permision(**chmod +x uninstall.sh**).
Run the uninstall script(**./uninstall.sh**).






# Note's for other developers that will read the code:
These scripts are 2 separate programs.
The vpn directory is the systemd service that controls the vpn.
The vpncontrol directory is the gui and trayicon that controls the vpn service with a unix socket.



├── install.sh # The install script
├── installTools # Tools used by install.sh
│   ├── setupAutostart.py # Creates trayicon on user login(The gui part. vpncontrol package)
│   └── setupService.py # Creates the service that controls the vpn(vpn package)
├── README
├── uninstall.sh # Uninstall script
├── vpn # Systemd service runs as root 
│   ├── main.py
│   ├── updater.py # Updates the nord ovpn files every 10 days
│   ├── uSocket.py # Unix socket for communication from vpncontrol(gui)
│   └── vpn.py # The code that handled the vpn and kill switch
└── vpncontrol
    ├── flags # Directory will hold images for the gui
    ├── helperFlaglist.py # Functions use by viewFlaglist.py gui. 
    ├── main.py
    ├── requirements.txt # Pip requirements for install.sh for creating a venv
    ├── uSocket.py # Unix socket for communication with vpn service
    ├── viewFlaglist.py # The gui where you can select a vpn server
    ├── viewTrayicon.py # The systems trayicon
    └── vpn.svg # Image used by trayicon


