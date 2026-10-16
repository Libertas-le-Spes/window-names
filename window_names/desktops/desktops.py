from .hyprland import Hyprland
from .i3 import I3
from .sway import Sway
from .x11 import X11

DESKTOPS = [Hyprland, Sway, I3, X11]


def running_desktop(desktops: list = DESKTOPS):
    found = next((desktop for desktop in desktops if desktop.is_running()), None)
    if found is None:
        raise SystemExit("window-names supports Hyprland, Sway, i3 and X11 desktops, and none of them is running here.")
    return found()
