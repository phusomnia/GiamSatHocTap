ui_fzf_menu() {
  local title="$1"
  shift
  local items=("$@")

  printf '%s\n' "${items[@]}" |
  fzf \
    --height 40% \
    --layout=reverse \
    --border \
    --prompt="⚡ $title > " \
    --no-sort \
    --header="TUI Framework"
}