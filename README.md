# window-names

With several terminals, two windows of the same IDE and a row of web apps open, nothing on screen says which window is which: titles are whatever each app chooses, and some desktops (Omarchy, for one) draw no title bars at all. window-names gives every window a name that tells it apart, and shows it where the desktop shows a window's title.

| Window | Name shown |
|---|---|
| Claude Code in a terminal | `Claude Code — ~ · Session window name display` (the folder, then Claude's session name) |
| Any other terminal | `Terminal — ~/RiderProjects/chronata`, or `nvim — …` while a program runs in it |
| A JetBrains IDE | `Rider — onplia` (the project) |
| A Chromium web app | `github.com` (the site) |
| Anything else | `Files — Downloads` (the app's name, then its own title) |

A name typed by hand wins over everything, then a name another tool gives the window, then the default above.

## Desktops

Each desktop shows a name its own way. Only the Hyprland part has run on a real desktop; the others have only been tested against stand-ins written from each desktop's documentation, so they have **not been tested for real**.

| Desktop | Where the name appears | Tested for real |
|---|---|---|
| Hyprland | a title bar on every window, drawn by a fork of hyprbars ([Libertas-le-Spes/hyprland-plugins](https://github.com/Libertas-le-Spes/hyprland-plugins), branch `set-title`, the change offered upstream in [hyprwm/hyprland-plugins#716](https://github.com/hyprwm/hyprland-plugins/pull/716)) | yes |
| Sway | the window's title bar, through Sway's `title_format` | no |
| i3 | the window's title bar, through i3's `title_format` | no |
| Other X11 desktops (XFCE, Cinnamon, MATE, …) | the window's own title, rewritten through `xprop` | no |
| GNOME, KDE | not supported: neither lets another program change a window's title | — |

Known gaps, none of them seen on a real desktop yet:

- **Chromium web apps on X11** may not be recognised as web apps, so they would show `Chromium — <page title>` instead of the site.
- **A `%` in a name on Sway or i3** may be read as one of their placeholders (`%title`, `%class`, …).
- **On X11**, an app that changes its own title (a terminal does, at every prompt) briefly shows that title until window-names puts the name back, within about a second.

## Hyprland: when Hyprland is updated

The title bars come from a Hyprland add-on, which has to be built for the exact Hyprland version installed. window-names rebuilds it by itself at the first login after a Hyprland update. If the new Hyprland changed too much for it to build, the bars disappear (the windows keep working) and a notification says so, until the fork is moved onto the upstream fix for that version.

## Install

```sh
./install.sh
```

It detects the running desktop, starts window-names at every login and binds **Super+Alt+R** to rename the focused window (on other X11 desktops, bind `~/.local/bin/window-names rename` yourself). Renaming asks with Omarchy's menu, zenity or kdialog, whichever the machine has. On X11 it needs `xprop` (package `xorg-xprop` or `x11-utils`).

`window-names show` prints every open window with the name it would get.

## Naming windows from another tool

Write the name, followed by a newline, to `~/.local/state/window-names/<window id>`: write a temporary file in that folder (its name starting with `.`) and rename it into place. The window id is Hyprland's address (`0x55d1a2b3c4d0`), Sway's or i3's container id, or the X11 window id. window-names deletes the file when the window closes. [Hiru Tsatsi](https://github.com/Libertas-le-Spes/hiru-tsatsi) names the apps it starts this way.
