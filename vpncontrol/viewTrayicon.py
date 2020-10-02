import gi, os, sys
from viewFlaglist import show as windows_flags
from uSocket import send, start_reciever

gi.require_version("Gtk", "3.0")
#gi.require_version("Notify", "0.7")

import signal
try:
    from gi.repository import Notify as notify
except:
    # Bug fix for raspberry pi 4 . gi.repository doesn't contain Notify
    from unittest.mock import MagicMock
    notify = MagicMock() # Making notify a stub that does nothing.
    
from gi.repository import Gtk

APP_ID = "vpn"
PATH_INSTALLED = os.path.join(os.path.expanduser("~"), ".nvpn")
SFILE = os.path.join(PATH_INSTALLED, ".autoconnect") # File existence enables auto connect on boot in none gui script
notify.init(APP_ID)


class sysicon(object):
    """System trayicon"""

    def __init__(self):
        self.menu = Gtk.Menu()
        self.s_icon = Gtk.StatusIcon()
        self.s_icon.set_from_file(os.path.join(os.path.dirname(__file__), "vpn.svg"))
        self.s_icon.set_tooltip_text("No vpn connection")
        self.s_icon.connect("popup-menu", self.right_click)
        start_reciever(
            notify.Notification.new, self.s_icon.set_tooltip_text
        )  # Communication between vpn and gui script.
        signal.signal(signal.SIGINT, self.Exit)
        self.buildmenu()
        Gtk.main()

    def buildmenu(self):
        def additem(title, command, sep=False):
            item = Gtk.MenuItem()
            item.set_label(title)

            item.connect("activate", command)
            self.menu.append(item)
            self.menu.show_all()
            if sep == True:
                separator = Gtk.SeparatorMenuItem()
                self.menu.append(separator)
                self.menu.show_all()

        additem("Connect to", lambda x: windows_flags())
        additem("Reconnect vpn", lambda x: send("reconnect"), sep=True)
        additem("Stop vpn", lambda x: send("stop"), sep=True)
        additem(
            "Enable autoconnect on boot"
            if not os.path.exists(SFILE)
            else "Disable autoconnect on boot",
            self.setAuto,
            sep=True,
        )

    def get_tray_menu(self):
        return self.menu

    def setAuto(self, item, *args):
        """
        Set vpn autostart on boot
        """
        label = item.get_label()
        if label == "Enable autoconnect on boot":
            open(SFILE, "w").close()
            item.set_label("Disable autoconnect on boot")
        else:
            os.remove(SFILE)
            item.set_label("Enable autoconnect on boot")

    def Exit(self, *args):
        send("stop")
        notify.uninit()
        Gtk.main_quit()

    def right_click(self, icon, button, time):
        self.get_tray_menu()

        def pos(*args):
            return Gtk.StatusIcon.position_menu(*args)

        self.menu.popup(None, None, pos, icon, button, time)
