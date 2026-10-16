local function theme_colors()
  local colors = {}
  local file = io.open(os.getenv("HOME") .. "/.local/state/omarchy/current/theme/colors.toml")
  if not file then
    return colors
  end
  for line in file:lines() do
    local key, value = line:match('^([%w_]+)%s*=%s*"(#%x+)"')
    if key then
      colors[key] = value
    end
  end
  file:close()
  return colors
end

local function hyprbars_loaded()
  for _, plugin in ipairs(hl.get_loaded_plugins()) do
    if plugin.name == "hyprbars" then
      return true
    end
  end
  return false
end

if hyprbars_loaded() then
  local colors = theme_colors()
  hl.config({
    plugin = {
      hyprbars = {
        bar_height = 22,
        bar_text_size = 10,
        bar_text_font = "JetBrainsMono Nerd Font",
        bar_color = colors.dark_background or "#161622",
        col = { text = colors.foreground or "#cdd6f4" },
        bar_precedence_over_border = true,
      },
    },
  })
end

o.launch_on_start(os.getenv("HOME") .. "/.local/bin/window-names run")
o.bind("SUPER + ALT + R", "Rename window", os.getenv("HOME") .. "/.local/bin/window-names rename")
