kill_all_python() {
  log_info "Finding Python processes..."

  case "$(os_type)" in
    windows)
      local pids
      pids=$(tasklist.exe //FI "IMAGENAME eq python.exe" //FO CSV | grep python.exe | cut -d',' -f2 | tr -d '"' | tr '\n' ' ')
      if [ -z "$pids" ]; then
        log_info "No Python processes found"
        return 0
      fi
      for pid in $pids; do
        taskkill.exe //F //PID "$pid"
      done
      ;;
    *)
      local pids
      pids=$(pgrep -f python 2>/dev/null)
      if [ -z "$pids" ]; then
        log_info "No Python processes found"
        return 0
      fi
      echo "$pids" | xargs kill -9
      ;;
  esac

  log_success "Killed all Python processes"
}

python_info() {
  echo "Python: $(python --version 2>/dev/null || python3 --version 2>/dev/null || echo 'not installed')"
  echo "Pip:    $(pip --version 2>/dev/null || pip3 --version 2>/dev/null || echo 'not installed')"
  echo "uv:     $(uv --version 2>/dev/null || echo 'not installed')"
  echo "Conda:  $(conda --version 2>/dev/null || echo 'not installed')"
}

python_init_venv() {
  local env_path="${1:-.venv}"

  if [ -d "$env_path" ]; then
    log_info "venv already exists: $env_path"
    python_activate "$env_path"
    return 0
  fi

  conda create -y -p "$env_path" python=3.12
  local rc=$?

  if [ $rc -eq 0 ]; then
    log_success "venv created: $env_path"
    python_activate "$env_path"
  else
    log_error "venv create failed (exit $rc)"
    return 1
  fi
}

python_activate() {
  local env_path="${1:-.venv}"

  if [ ! -d "$env_path" ]; then
    log_error "venv not found: $env_path"
    return 1
  fi

  if [ -f "$env_path/pyvenv.cfg" ]; then
    if [ "$(os_type)" = windows ]; then
      source "$env_path/Scripts/activate"
    else
      source "$env_path/bin/activate"
    fi
  elif [ -d "$env_path/conda-meta" ]; then
    if ! command -v conda &>/dev/null; then
      log_error "conda is not installed"
      return 1
    fi
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate "$env_path"
  else
    log_error "unknown venv type: $env_path"
    return 1
  fi
}

os_type() {
  case "$(uname -s)" in
    Linux*)  echo "linux" ;;
    Darwin*) echo "macos" ;;
    CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
    *)       echo "unknown" ;;
  esac
}

__python_exe() {
  local env_path="$1"
  case "$(os_type)" in
    windows)
      if [ -f "$env_path/Scripts/python.exe" ]; then
        printf "%s" "$env_path/Scripts/python.exe"
      elif [ -f "$env_path/python.exe" ]; then
        printf "%s" "$env_path/python.exe"
      else
        return 1
      fi
      ;;
    *)
      if [ -f "$env_path/bin/python" ]; then
        printf "%s" "$env_path/bin/python"
      else
        return 1
      fi
      ;;
  esac
}

python_install_requirements() {
  local env_path="${1:-.venv}"
  local requirements="${2:-requirements.txt}"

  if [ ! -f "$requirements" ]; then
    log_error "Missing requirements file: $requirements"
    return 1
  fi

  if [ ! -d "$env_path" ]; then
    log_info "venv missing, creating: $env_path"
    python_init_venv "$env_path" || return 1
  fi

  local python_exe
  python_exe=$(__python_exe "$env_path") || {
    log_error "Python executable not found in $env_path"
    return 1
  }

  uv pip install --python "$python_exe" -r "$requirements"
  local rc=$?
  spinner_stop

  if [ $rc -eq 0 ]; then
    log_success "Dependencies installed into $env_path"
  else
    log_error "pip install failed (exit $rc)"
    return 1
  fi
}

python_clear_venv() {
  local dir="${1:-python}"
  local venv_path="${2:-.venv}"

  if [ ! -d "$dir" ]; then
    log_error "Directory does not exist: $dir"
    return 1
  fi

  (
    cd "$dir" || exit 1

    if [ ! -d "$venv_path" ]; then
      log_info "No venv to clear: $dir/$venv_path"
      return 0
    fi

    rm -rf "$venv_path"
    log_success "Removed venv: $dir/$venv_path"
  )
}

python_build() {
  local dir="${1:-.}"
  local env_path="${2:-.venv}"

  if [ ! -d "$dir" ]; then
    log_error "Directory does not exist: $dir"
    return 1
  fi

  (
    cd "$dir" || exit 1
    local python_exe
    python_exe=$(__python_exe "$env_path") || {
      log_error "Python executable not found in $env_path"
      return 1
    }

    log_info "Compile check..."
    "$python_exe" -m compileall . -q -x ".venv|__pycache__"
    local rc=$?
    if [ $rc -eq 0 ]; then
      log_success "Build passed"
    else
      log_error "Build failed (exit $rc)"
      return 1
    fi
  )
}

python_run() {
  local dir="${1:-.}"
  local env_path="${2:-.venv}"
  local script="$3"

  if [ ! -d "$dir" ]; then
    log_error "Directory does not exist: $dir"
    return 1
  fi

  (
    cd "$dir" || exit 1
    local python_exe
    python_exe=$(__python_exe "$env_path") || {
      log_error "Python executable not found in $env_path"
      return 1
    }

    if [ ! -f "$script" ]; then
      log_error "Script not found: $script"
      return 1
    fi

    "$python_exe" "$script"
    local rc=$?
    if [ $rc -eq 0 ]; then
      log_success "Script finished: $script"
    else
      log_error "Script failed (exit $rc)"
      return 1
    fi
  )
}

python_fastapi_server() {
  local dir="${1:-demo/fastapi}"
  local config_file="${2:-app_config.yaml}"

  if [ ! -d "$dir" ]; then
    log_error "Directory does not exist: $dir"
    return 1
  fi

  dir="$(realpath "$dir")"

  if [ ! -f "$dir/$config_file" ]; then
    log_error "Config file not found: $dir/$config_file"
    return 1
  fi

  if ! command -v yq &>/dev/null; then
    log_error "yq is not installed"
    return 1
  fi

  local host port workers
  host=$(yq -r '.app.host // "127.0.0.1"' "$dir/$config_file")
  port=$(yq -r '.app.port // 8080' "$dir/$config_file")
  workers=$(yq -r '.app.workers // 4' "$dir/$config_file")

  local python_exe
  python_exe=$(__python_exe "$dir/.venv") || {
    log_error "Python executable not found in $dir/.venv"
    return 1
  }

  (
    cd "$dir" || exit 1
    uv run --with granian --python "$python_exe" \
      granian main:app \
      --interface asgi \
      --host "$host" \
      --port "$port" \
      --workers "$workers"
  )
}

python_run_server() {
  local dir="${1:-.}"
  local env_path="${2:-.venv}"
  local app_module="${3:-src.lain:app}"
  local host="${4:-127.0.0.1}"
  local port="${5:-8000}"

  if [ ! -d "$dir" ]; then
    log_error "Directory does not exist: $dir"
    return 1
  fi

  dir="$(realpath "$dir")"

  kill_all_python

  if lsof -Pi :"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
    log_error "Port $port is already in use"
    return 1
  fi

  local python_exe
  python_exe=$(__python_exe "$dir/$env_path") || {
    log_error "Python executable not found in $dir/$env_path"
    return 1
  }

  case "$(os_type)" in
    windows) python_exe="$(cygpath -w "$python_exe")" ;;
  esac

  unset SSL_CERT_FILE
  export PYTHONDONTWRITEBYTECODE=1

  (
    cd "$dir" || exit 1
    log_info "Starting server at http://$host:$port"
    bunx nodemon -e py --exec "$python_exe -m granian $app_module --interface asgi --host $host --port $port"
  )
}

python_server_pipeline() {
  local dir="${1:-.}"
  local env_path="${2:-.venv}"
  local req="${3:-src/requirements.txt}"
  local app_module="${4:-src.lain:app}"
  local host="${5:-127.0.0.1}"
  local port="${6:-8000}"

  if [ ! -d "$dir" ]; then
    log_error "Directory does not exist: $dir"
    return 1
  fi

  dir="$(realpath "$dir")"

  log_info "Pipeline: $dir — 3 stages"

  log_info "Stage 1/3: init — $dir/$env_path"
  python_init_venv "$dir/$env_path" || return 1

  log_info "Stage 2/3: install — $dir/$req"
  python_install_requirements "$dir/$env_path" "$dir/$req" || return 1

  log_info "Stage 3/3: run — $app_module"
  python_run_server "$dir" "$env_path" "$app_module" "$host" "$port" || return 1

  log_success "Pipeline complete: $dir"
}

python_demo_pipeline() {
  local dir="${1:-demo/python}"

  if [ ! -d "$dir" ]; then
    log_error "Directory does not exist: $dir"
    return 1
  fi

  dir="$(realpath "$dir")"
  local env_path="${2:-$dir/.venv}"
  local req="${3:-$dir/requirements.txt}"
  local demo_file="${4:-$dir/src/main.py}"

  log_info "Pipeline: $dir — 4 stages"

  # Stage 1: init
  log_info "Stage 1/4: init — $env_path"
  python_init_venv "$env_path" || return 1

  # Stage 2: install
  log_info "Stage 2/4: install — $req"
  python_install_requirements "$env_path" "$req" || return 1

  # Stage 3: build
  log_info "Stage 3/4: build"
  python_build "$dir" "$env_path" || return 1

  # Stage 4: run
  log_info "Stage 4/4: run — $demo_file"
  python_run "$dir" "$env_path" "$demo_file" || return 1

  log_success "Pipeline complete: $dir"
}

python_demo_fastapi_pipeline() {
  local dir="${1:-demo/fastapi}"

  if [ ! -d "$dir" ]; then
    log_error "Directory does not exist: $dir"
    return 1
  fi

  dir="$(realpath "$dir")"
  local env_path="${2:-$dir/.venv}"
  local req="${3:-$dir/requirements.txt}"

  log_info "Pipeline: $dir — 4 stages"

  # Stage 1: init
  log_info "Stage 1/4: init — $env_path"
  python_init_venv "$env_path" || return 1

  # Stage 2: install
  log_info "Stage 2/4: install — $req"
  python_install_requirements "$env_path" "$req" || return 1

  # Stage 3: build
  log_info "Stage 3/4: build"
  python_build "$dir" "$env_path" || return 1

  # Stage 4: run
  log_info "Stage 4/4: run — FastAPI server"
  python_fastapi_server "$dir" || return 1

  log_success "Pipeline complete: $dir"
}
