import os, json
from uSocket import send

COUNTRY_NAMES = {
    "al": "Albania",
    "ar": "Argentina",
    "au": "Australia",
    "at": "Austria",
    "be": "Belgium",
    "ba": "Bosnia and Herzegovina",
    "br": "Brazil",
    "bg": "Bulgaria",
    "ca": "Canada",
    "cl": "Chile",
    "cr": "Costa Rica",
    "hr": "Croatia",
    "cy": "Cyprus",
    "cz": "Czechia",
    "dk": "Denmark",
    "ee": "Estonia",
    "fi": "Finland",
    "fr": "France",
    "ge": "Georgia",
    "de": "Germany",
    "gr": "Greece",
    "hk": "Hong Kong",
    "hu": "Hungary",
    "is": "Iceland",
    "in": "India",
    "id": "Indonesia",
    "ie": "Ireland",
    "il": "Israel",
    "it": "Italy",
    "jp": "Japan",
    "kr": "Korea, Republic of",
    "lv": "Latvia",
    "lu": "Luxembourg",
    "mk": "Macedonia, The Former Yugoslav Republic Of",
    "my": "Malaysia",
    "mx": "Mexico",
    "md": "Moldova, Republic of",
    "nl": "Netherlands",
    "nz": "New Zealand",
    "no": "Norway",
    "pl": "Poland",
    "pt": "Portugal",
    "rs": "Republic of Serbia",
    "ro": "Romania",
    "sg": "Singapore",
    "sk": "Slovakia",
    "si": "Slovenia",
    "za": "South Africa",
    "es": "Spain",
    "se": "Sweden",
    "ch": "Switzerland",
    "tw": "Taiwan, Province of China",
    "th": "Thailand",
    "tr": "Turkey",
    "ua": "Ukraine",
    "uk": "United Kingdom",
    "us": "United States",
    "vn": "Vietnam",
}
PATH_BASE = os.path.split(os.path.abspath(__file__))[0]
PATH_FLAGS = os.path.join(PATH_BASE, "flags")
COUNTER_FILE = os.path.join(os.path.expanduser("~"), ".nvpn", "counter.json")


def get_flag_dict():
    """
    () -> {str: str}

    Returns all country names that have an img 
    """
    flag_files = {x.split(".")[0] for x in os.listdir(PATH_FLAGS)}
    return {k: v for k, v in COUNTRY_NAMES.items() if k in flag_files}


def _read_count_flag():
    """
    () -> {str: int}

    Read the counter file that counts the times a server location is selected.
    Returns location and count.
    """
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r") as r:
            data = json.load(r)
        return data
    else:
        with open(COUNTER_FILE, "w") as f:
            data = {k: 0 for k in get_flag_dict()}
            json.dump(data, f)
        return data


def _write_count_flag(flag):
    """
    (str) ->

    Updates the counter for a flag
    """
    data = _read_count_flag()
    if flag in data:
        data[flag] += 1
        with open(COUNTER_FILE, "w") as w:
            json.dump(data, w)


def flag_clicked(flag):
    """
    (str) ->

    Start action to count clicked flag.
    Send connect command to unix socket that controls the vpn.
    """

    _write_count_flag(flag)
    send(f"connect {flag}")


def get_sorted_flag_dict():
    """
    () -> {str: str}

    Sort function to return most clicked flags.
    Used by gui to display most used servers at the top.
    """
    temp = sorted(get_flag_dict().items(), key=lambda x: -_read_count_flag()[x[0]])
    return {k: v for k, v in temp}
