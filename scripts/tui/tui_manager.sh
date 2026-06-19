tui_run() {
  local menu_dir
  menu_dir="$(dirname "${BASH_SOURCE[0]}")"

  local items=()
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ -z "$line" ]] && continue
    items+=("$line")
  done < "$menu_dir/menu.txt"

  local choice
  choice=$(
    ui_fzf_menu "Menu" "${items[@]}"
  )

  [[ -z "$choice" ]] && exit 0
  [[ "$choice" == "exit" ]] && exit 0

  if declare -F "$choice" &>/dev/null; then
    "$choice"
  fi
}
