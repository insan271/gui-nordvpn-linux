import os, pickle, datetime, subprocess

PATH = os.path.dirname(__file__)

# Only using packages from the standard library. Script run as root. Reason for not using requests package.

def update():
    """
    Download/update nordvpn files.
    """
    url = "https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip"
    if _update_required():
        os.chdir(PATH)
        subprocess.run(f"curl -O {url}", shell=True)
        if os.path.exists("ovpn.zip"):
            subprocess.run("rm -r ovpn_tcp", shell=True)
            subprocess.run("rm -r ovpn_udp", shell=True)
            subprocess.run("unzip ovpn.zip", shell=True)
            os.remove("ovpn.zip")
            _config_vpnfiles()
            print("Update vpn files complete.") # Don't remove, install.sh is parsing stdout for this output.


def _update_required():
    """
    () -> bool

    Check update file for date to update.
    """
    now = datetime.datetime.now()
    if (
        not os.path.exists(os.path.join(PATH, "dateupdated"))
        or now > _get_date_from_pickle()
    ):
        with open(os.path.join(PATH, "dateupdated"), "wb") as f:
            pickle.dump(now, f)
        return True
    return False


def _get_date_from_pickle():
    """
    () -> datetime.datetime

    Returns the date update is required.
    """
    with open(os.path.join(PATH, "dateupdated"), "rb") as f:
        date = pickle.load(f)
        return date + datetime.timedelta(days=10)


def _config_vpnfiles():
    """
    Edit ovpn files to patch DNS leak.
    """
    path_ovpn = os.path.join(PATH, "ovpn_tcp")
    files = os.listdir(path_ovpn)
    for file in files:
        z = open(os.path.join(path_ovpn, file), "r")
        text = z.read()
        z.close()
        find = text.find("mute")
        find = text[find:].find("\n") + find
        textslpit1 = text[0 : find + 1]
        textsplit2 = text[find + 1 :]
        textinject = (
            textslpit1
            + "script-security 2\nup /etc/openvpn/update-resolv-conf\ndown /etc/openvpn/update-resolv-conf\n"
            + textsplit2
        )
        w = open(os.path.join(path_ovpn, file), "w")
        w.write(textinject)
        w.close()
