running() { [[ -n ${DISPLAY:-} && -z ${WAYLAND_DISPLAY:-} ]]; }

install_for_desktop() {
  command -v xprop >/dev/null || { echo "window-names needs xprop (package xorg-xprop or x11-utils)." >&2; return 1; }
  mkdir -p "$HOME/.config/autostart"
  ln -sfn "$here/install/window-names.desktop" "$HOME/.config/autostart/window-names.desktop"
  echo "Bind a key to '$HOME/.local/bin/window-names rename' in your desktop's keyboard settings to rename windows."
}
