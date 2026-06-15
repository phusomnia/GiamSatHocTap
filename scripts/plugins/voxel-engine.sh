VOXEL_ENGINE_DIR="$(pwd)/go"
VOXEL_ENGINE_BIN="bin/voxel-engine"
VOXEL_ENGINE_MODULE="voxel-engine"

voxel_engine_info() {
  local go_version
  go_version="$(go version 2>/dev/null || echo 'not installed')"
  echo "Voxel Engine: Go($go_version)"
  echo "Project:      $VOXEL_ENGINE_DIR"
  echo "Source:       $VOXEL_ENGINE_DIR/src"
  echo "Binary:       $VOXEL_ENGINE_DIR/$VOXEL_ENGINE_BIN$(platform_is_windows && echo '.exe')"
  echo "Pipeline:     init -> install -> build -> run"
}

voxel_engine_init() {
  log_info "[Stage 1/4] INIT"

  if [ -f "$VOXEL_ENGINE_DIR/go.mod" ]; then
    log_info "go.mod already exists, skipping init"
    return 0
  fi

  go_init_module "$VOXEL_ENGINE_DIR" "$VOXEL_ENGINE_MODULE"
}

voxel_engine_install() {
  log_info "[Stage 2/4] INSTALL"
  go_install_deps "$VOXEL_ENGINE_DIR" "dependencies"
}

voxel_engine_build() {
  log_info "[Stage 3/4] BUILD"
  go_build "$VOXEL_ENGINE_DIR" "$VOXEL_ENGINE_BIN"
}

voxel_engine_exec() {
  log_info "[Stage 4/4] RUN"
  go_run_binary "$VOXEL_ENGINE_DIR" "$VOXEL_ENGINE_BIN"
}

voxel_engine_run() {
  log_info "Starting Voxel Engine pipeline: init -> install -> build -> run"

  voxel_engine_init    || { log_error "Pipeline failed at INIT";    return 1; }
  voxel_engine_install || { log_error "Pipeline failed at INSTALL"; return 1; }
  voxel_engine_build   || { log_error "Pipeline failed at BUILD";   return 1; }
  voxel_engine_exec    || { log_error "Pipeline failed at RUN";     return 1; }

  log_success "Pipeline completed"
}

voxel_engine_clear_deps() {
  clear_deps "$VOXEL_ENGINE_DIR"
}

voxel_engine_dev() {
  log_info "Starting Voxel Engine dev mode: install -> run (go run)"

  voxel_engine_install || { log_error "Pipeline failed at INSTALL"; return 1; }

  go_run_src "$VOXEL_ENGINE_DIR" "./src"

  log_success "Dev session ended"
}
