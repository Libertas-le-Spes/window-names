#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"

make -C "$HOME/RiderProjects/hyprland-plugins/hyprbars" all
mkdir -p "$HOME/.local/bin"
ln -sfn "$here/bin/window-names" "$HOME/.local/bin/window-names"
ln -sfn "$here/hypr/titlebars.lua" "$HOME/.config/hypr/titlebars.lua"

if ! grep -q 'require("hypr.titlebars")' "$HOME/.config/hypr/hyprland.lua"; then
  printf '\nrequire("hypr.titlebars")\n' >> "$HOME/.config/hypr/hyprland.lua"
fi
