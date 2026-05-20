install_dbml() {
    bun add -g @dbml/cli
}

install_uv() {
    curl -LsSf https://astral.sh/uv/install.sh | sh
}

install_yq() {
    sudo apt install yq
}

install_venv() {
    read -p "Python version: " PY_VERSION
    conda create -p .venv "$VENV_DIR" python="$PY_VERSION"
    echo "Created $VENV_DIR"
}

activate_venv() {
    conda activate ./.venv
}
