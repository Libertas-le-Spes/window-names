# window-names

Omarchy windows have no title bars, so with several terminals, two Rider windows and a row of web apps there is nothing on screen saying which window is which. This puts a bar on every window and fills it with a name that tells them apart: `Rider — onplia`, `github.com`, `Claude Code — ~ · <session name>`.

Names come, in order, from a rename by hand (Super+Alt+R), from another tool such as Workbench writing `~/.local/state/window-names/<window address>`, or from the default for that kind of window.

The bars are drawn by a fork of hyprbars (`~/RiderProjects/hyprland-plugins`, branch `bar-text`) that accepts text from outside. It is rebuilt automatically when Hyprland is updated; if Hyprland changes in a way that breaks the build, the bars disappear and a notification says so, until the fork is moved onto upstream's fix.

Install with `./install.sh`.
