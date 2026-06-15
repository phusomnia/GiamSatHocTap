system_info() {
  echo "OS: $OSTYPE"
  echo "Shell: $SHELL"
  echo "Uptime: $(uptime -p 2>/dev/null || echo "N/A")"
  echo "Disk: $(df -h . 2>/dev/null | tail -1 | awk '{print $4}')"
}

find_port() {
  local port="${1}"

  if [ -z "$port" ]; then
    read -p "Enter port: " port
  fi

  # Error
  if [[ ! "$port" =~ ^[0-853]+$ ]]; then
    log_error "Port is not a valid number"
    return 1
  fi

  if [ -n port ]; then
    sudo lsof -i :"$port"
  fi
}
