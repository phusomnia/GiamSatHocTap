get_server_dir() {
  local path="${1:-}"
  if [ -z "$path" ]; then
    echo "$(pwd)"
  else
    echo "$(pwd)/${path}"
  fi
}

VOXEL_SERVER_DIR="$(get_server_dir python)"
VOXEL_SERVER_VENV=".venv"
VOXEL_SERVER_REQUIREMENTS="src/requirements.txt"
VOXEL_SERVER_APP="lain:app"
VOXEL_SERVER_HOST="127.0.0.1"
VOXEL_SERVER_PORT="8000"

voxel_server_info() {
  local py_version
  local uv_version

  py_version="$(python --version 2>/dev/null || python3 --version 2>/dev/null || echo 'not installed')"
  uv_version="$(uv --version 2>/dev/null || echo 'not installed')"

  echo "Voxel Server: Python($py_version), uv($uv_version)"
  echo "Project:      $VOXEL_SERVER_DIR"
  echo "Source:       $VOXEL_SERVER_DIR/src"
  echo "App:          $VOXEL_SERVER_APP"
  echo "Address:      $VOXEL_SERVER_HOST:$VOXEL_SERVER_PORT"
  echo "Venv:         $VOXEL_SERVER_DIR/$VOXEL_SERVER_VENV"
  echo "Pipeline:     init -> install -> run"
}

voxel_server_init() {
  log_info "[Stage 1/3] INIT"

  if [ -d "$VOXEL_SERVER_DIR/$VOXEL_SERVER_VENV" ]; then
    log_info "venv already exists, skipping init"
    return 0
  fi

  python_init_venv "$VOXEL_SERVER_DIR" "$VOXEL_SERVER_VENV"
}

voxel_server_install() {
  log_info "[Stage 2/3] INSTALL"
  python_install_deps "$VOXEL_SERVER_DIR" "$VOXEL_SERVER_VENV" "$VOXEL_SERVER_REQUIREMENTS"
}

voxel_server_exec() {
  log_info "[Stage 3/3] RUN"
  python_run_server "$VOXEL_SERVER_DIR" "$VOXEL_SERVER_VENV" \
    "$VOXEL_SERVER_APP" "$VOXEL_SERVER_HOST" "$VOXEL_SERVER_PORT"
}

voxel_server_run() {
  log_info "Starting Voxel Server pipeline: init -> install -> run"

  voxel_server_init    || { log_error "Pipeline failed at INIT";    return 1; }
  voxel_server_install || { log_error "Pipeline failed at INSTALL"; return 1; }
  voxel_server_exec    || { log_error "Pipeline failed at RUN";     return 1; }

  log_success "Pipeline completed"
}

voxel_server_clear() {
  python_clear_venv "$VOXEL_SERVER_DIR" "$VOXEL_SERVER_VENV"
}

voxel_server_dev() {
  log_info "Starting Voxel Server dev mode: install -> run"

  voxel_server_install || { log_error "Pipeline failed at INSTALL"; return 1; }

  python_run_server "$VOXEL_SERVER_DIR" "$VOXEL_SERVER_VENV" \
    "$VOXEL_SERVER_APP" "$VOXEL_SERVER_HOST" "$VOXEL_SERVER_PORT"

  log_success "Dev session ended"
}
