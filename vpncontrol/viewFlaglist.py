import gi, os
from helperFlaglist import get_sorted_flag_dict, flag_clicked

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

PATH_BASE = os.path.split(os.path.abspath(__file__))[0]
PATH_FLAGS = os.path.join(PATH_BASE, "flags")


class FlowBoxWindow(Gtk.Window):
    """
    Gui window for selecting a vpn server.
    """
    def __init__(self):
        Gtk.Window.__init__(self, title="Connect to")
        self.set_border_width(10)
        self.set_default_size(800, 800)

        header = Gtk.HeaderBar(title="Select a server:")
        header.props.show_close_button = True

        self.set_titlebar(header)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        flowbox = Gtk.FlowBox()
        flowbox.set_valign(Gtk.Align.START)
        flowbox.set_max_children_per_line(30)
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

        self.create_flowbox(flowbox)

        scrolled.add(flowbox)

        self.add(scrolled)
        self.show_all()

    def create_flowbox(self, flowbox):
        for k, v in get_sorted_flag_dict().items():
            org_k = k
            if k == 'gb': k = "uk"
            img = Gtk.Image.new_from_file(os.path.join(PATH_FLAGS, f"{k}.png"))
            label = Gtk.Label(v.split(",")[0])
            button = Gtk.Button()
            grid = Gtk.Grid()
            grid.attach(img, 0, 0, 1, 1)
            grid.attach(label, 0, 1, 1, 1)
            grid.show_all()
            button.add(grid)
            button.connect("clicked", self.button_clicked, org_k)

            flowbox.add(button)

    def button_clicked(self, widget, flag):
        """
        Click handler for button.
        Button connect's to selected vpn server
        """
        flag_clicked(flag)
        self.destroy()


def show():
    """
    Display the gui windows for selecting a vpn server.
    """
    win = FlowBoxWindow()
    win.show_all()
