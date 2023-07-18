import os, pickle, datetime, logging, urllib.request

from pathlib import Path

PATH = Path(__file__).parents[1]

# Only using packages from the standard library. Script run as root. Reason for not using requests package.
def force_update():
        try:
            req = urllib.request.urlopen("https://airvpn.org/api/status/")
            if req.code == 200:
                with open(os.path.join(PATH, 'airvpn.json'), "w") as f:
                    f.write(req.read().decode())
                    logging.info(
                        "Update vpn files complete."
                    ) 
        except: pass

def update():
    """
    Download airvpn server list.
    """
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

