running() { [[ -n ${I3SOCK:-} ]]; }

install_for_desktop() {
  mkdir -p "$HOME/.config/i3/config.d"
  ln -sfn "$here/install/i3.conf" "$HOME/.config/i3/config.d/window-names"
  add_line_once "include $HOME/.config/i3/config.d/window-names" "$HOME/.config/i3/config"
  i3-msg reload >/dev/null
}
