kill_all_python() {
    print_info "Finding Python processes..."

    if is_windows; then
        PYTHON_PIDS=$(
            tasklist.exe //FI "IMAGENAME eq python.exe" //FO CSV |
            grep python.exe |
            cut -d',' -f2 |
            tr -d '"' |
            tr '\n' ' '
        )

        if [ -z "$PYTHON_PIDS" ]; then
            print_info "No Python processes found"
            return 0
        fi

        for pid in $PYTHON_PIDS; do
            taskkill.exe //F //PID "$pid"
        done

    else
        PYTHON_PIDS=$(pgrep -f python)

        if [ -z "$PYTHON_PIDS" ]; then
            print_info "No Python processes found"
            return 0
        fi

        echo "$PYTHON_PIDS" | xargs kill -9
    fi

    print_success "Killed all Python processes"
}

kill_port() {
    echo -n "Nhập port cần kill: "
    read PORT

    if [ -z "$PORT" ]; then
        print_error "Port không được để trống"
        return -1
    fi

    if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
        print_error "Port phải là số"
        return -1
    fi

    print_info "Đang tìm process trên port $PORT..."

    PID=$(lsof -ti :"$PORT" 2>/dev/null)

    if [ -z "$PID" ]; then
        print_warning "Không có process nào đang chạy trên port $PORT"
        return 0
    fi

    print_info "Tìm thấy PID: $PID"
    print_info "Đang kill process..."

    kill -9 "$PID" 2>/dev/null

    if [ $? -eq 0 ]; then
        print_success "Đã kill port $PORT (PID: $PID)"
    else
        print_error "Không thể kill process. Thử với sudo..."
        sudo kill -9 "$PID" 2>/dev/null
        if [ $? -eq 0 ]; then
            print_success "Đã kill port $PORT với sudo (PID: $PID)"
        else
            print_error "Không thể kill process $PID"
            return -1
        fi
    fi
}

run_streamlit_app() {
    is_conda_base && print_error "Please activate a conda environment first" && return 1
    
    export PYTHONDONTWRITEBYTECODE=1

    [ ! -d "frontend" ] && print_error "Frontend not found" && return 1

    python -m streamlit run frontend/app.py --server.address 127.0.0.1 --server.port 3000 --server.headless true
}

run_server_with_granian() {
    unset SSL_CERT_FILE
    export PYTHONDONTWRITEBYTECODE=1

    is_conda_base && print_error "Please activate a conda environment first" && return 1
    # check_and_install_missing || return 1

    CONFIG="src/config/app-config.yaml"

    if [ ! -f "$CONFIG" ]; then
        print_error "Can't find config file: $CONFIG"
        return -1
    fi

    HOST=$(yq -r '.app.host' "$CONFIG" 2>/dev/null)
    PORT=$(yq -r '.app.port' "$CONFIG" 2>/dev/null)

    if [ -z "$HOST" ] || [ "$HOST" = "null" ]; then
        print_error "Can't read app.host from yaml"
        return -1
    fi

    if [ -z "$PORT" ] || [ "$PORT" = "null" ]; then
        print_error "Can't read app.host from yaml"
        return -1
    fi

    print_info "Kiểm tra import lỗi..."

    print_info "Kill tất cả Python processes..."
    kill_all_python

    print_info "Kiểm tra port $PORT..."
    if lsof -Pi :"$PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $PORT đang được sử dụng!"
        echo -n "Có muốn kill process không? (y/n): "
        read answer
        if [[ "$answer" =~ ^[Yy]$ ]]; then
            kill -9 "$(lsof -ti :"$PORT")" 2>/dev/null
            sleep 1
        else
            print_error "Hủy khởi động server"
            return -1
        fi
    fi

    print_success "Start server at http://$HOST:$PORT"
    if [ -f ".venv/python.exe" ]; then
        bunx nodemon -e py --exec "./.venv/python.exe -m granian src.lain:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --interface asgi"
    elif [ -f ".venv/Scripts/python.exe" ]; then
        bunx nodemon -e py --exec "./.venv/Scripts/python.exe -m granian src.lain:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --interface asgi"
    elif [ -f ".venv/bin/python" ]; then
        bunx nodemon -e py --exec "./.venv/bin/python -m granian src.lain:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --interface asgi"
    else
        print_error "Python executable not found in .venv"
        return -1
    fi
}
