go_info() {
  echo "Go: $(go version 2>/dev/null || echo 'not installed')"
}

go_init_module() {
  local path_module="${1:-.}"
  local name_module="${2}"

  if [ ! -d "$path_module" ]; then
    log_error "Directory does not exist: $path_module"
    return 1
  fi

  cd "$path_module" || return 1

  if [ -f "go.mod" ]; then
    log_info "go.mod already exists"
    return 0
  fi

  if [ -z "$name_module" ]; then
    name_module="$(basename "$(pwd)")"
    if [ "$name_module" = "go" ]; then
      name_module="$(basename "$(dirname "$(pwd)")")"
    fi
  fi

  go mod init "$name_module"
}

go_install_deps() {
  local dir="${1:-.}"
  local deps_file="${2:-dependencies}"

  if [ ! -d "$dir" ]; then
    log_error "Directory does not exist: $dir"
    return 1
  fi

  (
    cd "$dir" || exit 1

    log_info "Installing Go dependencies..."

    go mod tidy
    if [ $? -eq 0 ]; then
      log_success "Dependencies installed"
    else
      log_error "Failed to install dependencies"
    fi

    if [ -f "$deps_file" ]; then
      log_info "Installing Go tools from $deps_file..."

      while IFS= read -r pkg || [ -n "$pkg" ]; do
        pkg="$(echo "$pkg" | xargs)"

        [ -z "$pkg" ] && continue
        [[ "${pkg#\#}" != "$pkg" ]] && continue

        log_info "  Installing $pkg..."

        if [[ "$pkg" == */cmd/* ]]; then
          go install "$pkg"
        else
          go get "$pkg"
        fi

        if [ $? -eq 0 ]; then
          log_success "  $pkg installed"
        else
          log_error "  Failed to install $pkg"
        fi
      done < "$deps_file"
    fi
  )
}

clear_deps() {
  local dir="${1:-.}"

  if [ ! -d "$dir" ]; then
    log_error "Directory does not exist: $dir"
    return 1
  fi

  (
    cd "$dir" || exit 1

    go clean -modcache
    log_success "Module cache cleared"
  )
}

create_api_spec() {
  apispec -d . -o specs/openapi.yaml
}

go_build() {
  local dir="${1:-.}"
  local output="${2:-bin/voxel-engine}"

  if [ ! -d "$dir" ]; then
    log_error "Directory does not exist: $dir"
    return 1
  fi

  (
    cd "$dir" || exit 1

    if platform_is_windows; then
      output="${output}.exe"
    fi

    mkdir -p "$(dirname "$output")"

    log_info "Building Go binary to $output..."

    go build -o "$output" ./src
    local rc=$?

    if [ $rc -eq 0 ]; then
      log_success "Binary built: $dir/$output"
    else
      log_error "Build failed (exit $rc)"
      return 1
    fi
  )
}

go_run_src() {
  local dir="${1:-.}"
  local src_path="${2:-./src}"

  if [ ! -d "$dir" ]; then
    log_error "Directory does not exist: $dir"
    return 1
  fi

  (
    cd "$dir" || exit 1

    log_info "Running $src_path directly (dev mode)..."
    go run "$src_path"
  )
}

go_run_binary() {
  local dir="${1:-.}"
  local binary="${2:-bin/voxel-engine}"

  if [ ! -d "$dir" ]; then
    log_error "Directory does not exist: $dir"
    return 1
  fi

  (
    cd "$dir" || exit 1

    if platform_is_windows; then
      binary="${binary}.exe"
    fi

    if [ ! -f "$binary" ]; then
      log_error "Binary not found: $dir/$binary"
      log_info "Run 'voxel_engine_build' first"
      return 1
    fi

    log_info "Running $binary..."
    "./$binary"
  )
}

go_demo_pipeline() {
  local dir="${1:-demo/go}"

  if [ ! -d "$dir" ]; then
    log_error "Directory does not exist: $dir"
    return 1
  fi

  dir="$(realpath "$dir")"

  log_info "Pipeline: $dir — 4 stages"

  # Stage 1: init
  log_info "Stage 1/4: init — go mod init"
  go_init_module "$dir" "demo" || return 1

  # Stage 2: install
  log_info "Stage 2/4: install — go mod tidy"
  go_install_deps "$dir" "" || return 1

  # Stage 3: build
  log_info "Stage 3/4: build"
  go_build "$dir" "bin/demo" || return 1

  # Stage 4: run
  log_info "Stage 4/4: run"
  go_run_src "$dir" "./src" || return 1

  log_success "Pipeline complete: $dir"
}