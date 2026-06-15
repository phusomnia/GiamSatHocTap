# Scripts

## Folder structure

```
scripts/
├── Scripts.md           # This file
├── kernel/
│   └── core.sh          # Colors, Spring Boot-style logger (log_info/log_error/log_warn/log_success/log_debug), spinner, platform, terminal utils
├── tui/
│   ├── ui.sh            # fzf menu UI wrapper
│   ├── tui_manager.sh   # Two-level category navigator (parses menu.txt)
│   └── menu.txt         # Menu data: ## headers = categories, items = commands
└── plugins/
    ├── system.sh        # system script
    ├── git.sh           # git script
    ├── python.sh        # python venv, install, pipeline, cross-platform
    ├── docker.sh        # docker script
    ├── nodejs.sh        # nodejs script
    ├── bun.sh           # bun script
    ├── go.sh            # go script
    ├── dotnet.sh        # dotnet script
    ├── nim.sh           # nim script
    ├── voxel-engine.sh  # voxel engine script
    ├── voxel-server.sh  # voxel server script
    └── debian.sh        # debian script
```

## How it works

`./script.sh` sources all `.sh` files from `kernel/`, `tui/`, and `plugins/`, then calls `tui_run()`.

### Menu flow

```
Categories → pick one → sub-commands → back/Esc → categories
                                        → execute → exit
```

1. Reads `menu.txt` — lines starting with `##` are category headers, others are commands
2. Shows categories in fzf (`exit` to quit)
3. Pick a category → shows its sub-commands
4. `back` / `Esc` returns to categories; pick a command → execute → exit

### menu.txt format

```
## Category Name
command_name
another_command

## Next Category
some_command
```

Lines starting with `##` become category items in the top-level fzf menu. Non-blank lines under each header become the sub-commands for that category.

### Adding a command

1. Add the item name to `menu.txt` under the appropriate `##` category
2. Define the function in the corresponding plugin file under `scripts/plugins/`

## Cross-platform support (`os_type`)

Defined in `plugins/python.sh`, usable by any sourced plugin:

- `os_type` — detects the current OS: `linux`, `macos`, `windows`, or `unknown`

```bash
case "$(os_type)" in
  windows) source "$env_path/Scripts/activate" ;;
  *)       source "$env_path/bin/activate" ;;
esac
```

On **Windows** 
- (detected via `CYGWIN*|MINGW*|MSYS*` from `uname -s`), Python venvs use `Scripts/` directory; on Unix they use `bin/`. The internal helper `__python_exe()` wraps this to locate `python` / `python.exe` inside a venv, so `python_install_requirements`, `python_fastapi_server`, and `python_demo_pipeline` work without modification on both platforms.