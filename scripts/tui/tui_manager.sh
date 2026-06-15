tui_run() {
  local menu_dir
  menu_dir="$(dirname "${BASH_SOURCE[0]}")"

  local cats=()
  local -a cmds
  local current_cat=""
  local idx=-1

  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ -z "$line" ]] && continue
    if [[ "$line" == "## "* ]]; then
      current_cat="${line#\#\# }"
      cats+=("$current_cat")
      idx=$((idx + 1))
      cmds[$idx]=""
    elif [[ "$idx" -ge 0 && "$line" != "exit" ]]; then
      cmds[$idx]+="$line"$'\n'
    fi
  done < "$menu_dir/menu.txt"

  while true; do
    local category
    category=$(
      ui_fzf_menu "Categories" "${cats[@]}" "exit"
    )
    [[ -z "$category" ]] && break
    [[ "$category" == "exit" ]] && break

    local cat_idx=-1
    for i in "${!cats[@]}"; do
      if [[ "${cats[$i]}" == "$category" ]]; then
        cat_idx=$i
        break
      fi
    done
    [[ $cat_idx -eq -1 ]] && continue

    local items=()
    while IFS= read -r cmd; do
      [[ -n "$cmd" ]] && items+=("$cmd")
    done <<< "${cmds[$cat_idx]}"
    items+=("back")

    local choice
    choice=$(
      ui_fzf_menu "$category" "${items[@]}"
    )
    [[ -z "$choice" ]] && continue
    [[ "$choice" == "back" ]] && continue

    if declare -F "$choice" &>/dev/null; then
      "$choice"
    fi
    break
  done
}
