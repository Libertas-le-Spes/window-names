running() { [[ -n ${HYPRLAND_INSTANCE_SIGNATURE:-} ]]; }

install_for_desktop() {
  make -C "$HOME/RiderProjects/hyprland-plugins/hyprbars" all
  ln -sfn "$here/install/hyprland.lua" "$HOME/.config/hypr/titlebars.lua"
  add_line_once 'require("hypr.titlebars")' "$HOME/.config/hypr/hyprland.lua"
}
