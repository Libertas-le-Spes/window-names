running() { [[ -n ${SWAYSOCK:-} ]]; }

install_for_desktop() {
  mkdir -p "$HOME/.config/sway/config.d"
  ln -sfn "$here/install/sway.conf" "$HOME/.config/sway/config.d/window-names"
  add_line_once "include $HOME/.config/sway/config.d/window-names" "$HOME/.config/sway/config"
  swaymsg reload >/dev/null
}
