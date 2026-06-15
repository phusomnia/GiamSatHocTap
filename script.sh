#!/usr/bin/env bash

SCRIPT_DIR="$(pwd)"

for k4l in "$SCRIPT_DIR"/scripts/kernel/*.sh; do
  source "$k4l"
done
for t1i in "$SCRIPT_DIR"/scripts/tui/*.sh; do
  source "$t1i"
done
for p4n in "$SCRIPT_DIR"/scripts/plugins/*.sh; do
  source "$p4n"
done

# ==========================================
# MAIN
# ==========================================
main() {
  tui_run
}

main