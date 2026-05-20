menu_options=(
    'run_server_with_granian'
    'run_streamlit_app'
    'clean_pycache'
    'kill_all_python'
    'kill_port'
    '── ENVIRONMENT ──'
    'install_venv'
    'activate_venv'
    '── PACKAGES ──'
    'check_and_install_missing'
    'install_packages'
    'uninstall_python_packages'
    'uninstall_all_packages'
    '── SYSTEM ──'
    'install_uv'
    'install_yq'
    '── OTHER ──'
    'install_dbml'
    'convert_dbml_to_sql'
    'convert_sql_to_orm'
    'check_size'
    'clean_uploads'
)

menu() {
    local choice cmd

    choice=$(
        printf '%s\n' "${menu_options[@]}" | \
        fzf --height 40% \
            --layout=reverse \
            --border \
            --prompt="⚡ Action: " \
            --info=inline \
            --no-sort \
            --header="Chọn action, dòng có dấu ── là header" \
            --color="border:#5f5fff,header:#af87ff,prompt:#5fff87,pointer:#ff5f87"
    )

    [[ -z "$choice" ]] && return
    [[ "$choice" == ──* ]] && return

    cmd="$(echo "$choice" | xargs)"
    "$cmd"
}
