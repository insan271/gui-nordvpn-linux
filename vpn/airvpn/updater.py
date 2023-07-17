import os, pickle, datetime, subprocess, logging, urllib.request, json

PATH = os.path.abspath(os.path.join('__file__', '..'))


# Only using packages from the standard library. Script run as root. Reason for not using requests package.
def force_update():
        try:
            req = urllib.request.urlopen(url)
            if req.code == 200:
                with open(os.path.join(PATH, 'airvpn.json'), "w") as f:
                    json.dump(req.read().decode(), f)
                    logging.info(
                        "Update vpn files complete."
                    ) 
        except: pass

def update():
    """
    Download airvpn server list.
    """
    url = "https://airvpn.org/api/status/"
    if _update_required():
        force_update()



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

