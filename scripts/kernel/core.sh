#!/bin/bash

# ==========================================
# COLORS
# ==========================================
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
CYAN="\033[0;36m"
PURPLE="\033[0;35m"

BOLD="\033[1m"
DIM="\033[2m"
NC="\033[0m"

# ==========================================
# LOGGER
# ==========================================
_LOG_BUF=()
_LOG_MAX_LEVEL=0
_LOG_MAX_PID=0
_LOG_MAX_THREAD=0
_LOG_MAX_FILE=0

_log_print() {
  printf "%s ${2}%*s${NC} ${PURPLE}%*s${NC} --- [%-*s] %-*s: %s\n" \
    "$1" "$_LOG_MAX_LEVEL" "$3" "$_LOG_MAX_PID" "$4" \
    "$_LOG_MAX_THREAD" "$5" "$_LOG_MAX_FILE" "$6" "$7"
}

_log() {
  local level="$1" color="$2" message="$3"
  local acstime pid thread file_name
  acstime="$(date -Iseconds 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%S%z)"
  pid="$$"
  thread="${FUNCNAME[2]:-$$}"
  file_name="$(basename "${BASH_SOURCE[2]:-unknown}")"

  local changed=0
  ((${#level} > _LOG_MAX_LEVEL)) && _LOG_MAX_LEVEL=${#level} && changed=1
  ((${#pid} > _LOG_MAX_PID)) && _LOG_MAX_PID=${#pid} && changed=1
  ((${#thread} > _LOG_MAX_THREAD)) && _LOG_MAX_THREAD=${#thread} && changed=1
  ((${#file_name} > _LOG_MAX_FILE)) && _LOG_MAX_FILE=${#file_name} && changed=1

  _LOG_BUF+=("$acstime"$'\t'"$level"$'\t'"$color"$'\t'"$pid"$'\t'"$thread"$'\t'"$file_name"$'\t'"$message")
  local n=${#_LOG_BUF[@]}

  if ((changed)) && ((n > 1)) && [[ -t 1 ]]; then
    for ((i = 1; i < n; i++)); do 
      printf "\033[A\033[K"; 
    done
    for entry in "${_LOG_BUF[@]}"; do
      IFS=$'\t' read -r t l c p th f m <<< "$entry"
      _log_print "$t" "$c" "$l" "$p" "$th" "$f" "$m"
    done
  else
    _log_print "$acstime" "$color" "$level" "$pid" "$thread" "$file_name" "$message"
  fi
}

log_success() { _log "SUCCESS" "${GREEN}${BOLD}" "$*"; }
log_error()   { _log "ERROR"   "${RED}${BOLD}"   "$*" >&2; }
log_warn()    { _log "WARN"    "${YELLOW}${BOLD}" "$*"; }
log_info()    { _log "INFO"    "${CYAN}${BOLD}"  "$*"; }
log_debug()   { _log "DEBUG"   "${DIM}"          "$*"; }

# ==========================================
# SPINNER
# ==========================================
SPINNER_CHARS=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏')
SPINNER_DELAY=0.1
SPINNER_START_TIME=0
SPINNER_PID=""

spinner_start() {
  local message="${1:-Loading...}"

  SPINNER_START_TIME=$SECONDS

  (
    while true; do
      local elapsed=$((SECONDS - SPINNER_START_TIME))

      for char in "${SPINNER_CHARS[@]}"; do
        printf "\r${CYAN}${BOLD}%s${NC} %s ${DIM}(%ss)${NC}" \
          "$char" \
          "$message" \
          "$elapsed"

        sleep "$SPINNER_DELAY"
      done
    done
  ) &

  SPINNER_PID=$!
}

spinner_stop() {
  if [[ -n "$SPINNER_PID" ]]; then
    kill "$SPINNER_PID" 2>/dev/null
    wait "$SPINNER_PID" 2>/dev/null
    SPINNER_PID=""
  fi

  printf "\r\033[K"
}

# ==========================================
# PLATFORM
# ==========================================
platform_os() {
  echo "$OSTYPE"
}

platform_is_windows() {
  [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]
}

platform_is_linux() {
  [[ "$OSTYPE" == linux* ]]
}

platform_is_macos() {
  [[ "$OSTYPE" == darwin* ]]
}

# ==========================================
# TERMINAL
# ==========================================
terminal_clear_line() {
  printf "\r\033[K"
}

terminal_hide_cursor() {
  tput civis
}

terminal_show_cursor() {
  tput cnorm
}