#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"

add_line_once() {
  grep -qxF "$1" "$2" 2>/dev/null || printf '\n%s\n' "$1" >> "$2"
}

mkdir -p "$HOME/.local/bin"
ln -sfn "$here/bin/window-names" "$HOME/.local/bin/window-names"

for desktop in hyprland sway i3 x11; do
  if (source "$here/install/$desktop.sh" && running); then
    source "$here/install/$desktop.sh"
    install_for_desktop
    echo "Installed for $desktop. It starts with your next login."
    exit 0
  fi
done

echo "window-names supports Hyprland, Sway, i3 and X11 desktops, and none of them is running here." >&2
exit 1
