install_packages() {
    if is_conda_base; then
        print_error "Cannot install packages in base conda environment!"
        print_info "Please create and activate a new conda environment first:"
        print_info "  conda create -n myenv python=3.11"
        print_info "  conda activate myenv"
        return -1
    fi

    print_info "Installing packages from requirements.txt..."

    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found"
        return -1
    fi

    uv pip install -r requirements.txt

    if [ $? -eq 0 ]; then
        print_success "Packages installed successfully"
    else
        print_error "Failed to install packages"
        return -1
    fi
}

check_and_install_missing() {
    if [ ! -f "requirements.txt" ]; then
        print_warning "requirements.txt not found, skipping auto-install"
        return 0
    fi

    local missing=()
    local installed_list

    installed_list=$(pip list --format=freeze 2>/dev/null | cut -d'=' -f1 | tr '[:upper:]' '[:lower:]')

    while IFS= read -r line || [ -n "$line" ]; do
        line=$(echo "$line" | xargs)
        [ -z "$line" ] && continue
        [[ "$line" == \#* ]] && continue
        [[ "$line" == -* ]] && continue

        pkg=$(echo "$line" | cut -d'[' -f1 | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | cut -d'~' -f1 | tr '[:upper:]' '[:lower:]')
        [ -z "$pkg" ] && continue

        if ! echo "$installed_list" | grep -qw "$pkg"; then
            missing+=("$line")
        fi
    done < "requirements.txt"

    if [ ${#missing[@]} -eq 0 ]; then
        print_success "All packages are installed"
        return 0
    fi

    print_warning "Missing packages detected:"
    for pkg in "${missing[@]}"; do
        echo "  - $pkg"
    done

    echo ""
    echo -n "Install missing packages? (Y/n): "
    read -r answer
    if [[ "$answer" =~ ^[Nn]$ ]]; then
        print_warning "Skipping package installation"
        return 1
    fi

    print_info "Installing missing packages..."
    for pkg in "${missing[@]}"; do
        print_info "Installing $pkg..."
        pip install "$pkg" 2>/dev/null || pip install --quiet "$pkg" 2>/dev/null
        if [ $? -eq 0 ]; then
            print_success "$pkg installed"
        else
            print_error "Failed to install $pkg"
        fi
    done

    print_success "Done installing missing packages"
}

uninstall_python_packages() {
    echo -n "Package name to uninstall: "
    read PACKAGE_NAME

    if [ -z "$PACKAGE_NAME" ]; then
        print_error "Package name cannot be empty"
        return -1
    fi

    print_info "Uninstalling $PACKAGE_NAME..."
    pip uninstall -y "$PACKAGE_NAME"

    if [ $? -eq 0 ]; then
        print_success "Successfully uninstalled $PACKAGE_NAME"
    else
        print_error "Failed to uninstall $PACKAGE_NAME"
        return -1
    fi
}

uninstall_all_packages() {
    print_warning "This will uninstall ALL Python packages!"
    echo -n "Are you sure? (y/n): "
    read confirm

    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        print_info "Cancelled"
        return 0
    fi

    print_info "Getting list of installed packages..."
    PACKAGES=$(pip list --format=freeze | grep -v "^pip=" | grep -v "^setuptools=" | cut -d'=' -f1)

    if [ -z "$PACKAGES" ]; then
        print_info "No packages to uninstall"
        return 0
    fi

    print_info "Uninstalling all packages..."
    echo "$PACKAGES" | xargs pip uninstall -y

    if [ $? -eq 0 ]; then
        print_success "Successfully uninstalled all packages"
    else
        print_error "Failed to uninstall some packages"
        return -1
    fi
}
