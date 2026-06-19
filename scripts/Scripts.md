# Scripts

## Folder structure

```
scripts/
├── Scripts.md           # This file
├── kernel/
│   └── core.sh          # Colors, Spring Boot-style logger (log_info/log_error/log_warn/log_success/log_debug), spinner, platform, terminal utils
├── tui/
│   ├── ui.sh            # fzf menu UI wrapper
│   ├── tui_manager.sh   # Flat menu runner (parses menu.txt, shows all items in one fzf list)
│   └── menu.txt         # Flat list of commands (one per line)
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
    ├── java.sh          # java script
    ├── php.sh           # php script
    ├── voxel-engine.sh  # voxel engine script
    ├── voxel-server.sh  # voxel server script
    └── debian.sh        # debian script
```

## How it works

`./script.sh` sources all `.sh` files from `kernel/`, `tui/`, and `plugins/`, then calls `tui_run()`.

### Menu flow

```
Flat menu → pick a command → execute → exit
                      → Esc → exit
```

1. Reads `menu.txt` — each line is a command name
2. Shows all commands in a single fzf menu (`exit` to quit)
3. Pick a command → execute → exit

### menu.txt format

```
command_name
another_command
exit
```

Every non-blank line is a command shown in the menu. The special `exit` item quits.

### Adding a command

1. Add the function name to `menu.txt`
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
