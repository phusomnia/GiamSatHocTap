#!/usr/bin/env bash

#
# conda search python
# conda remove -n myenv --all
# conda env export > environment.yml
# conda env create -f environment.yml
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPT_DIR/scripts/core.sh"
source "$SCRIPT_DIR/scripts/env.sh"
source "$SCRIPT_DIR/scripts/packages.sh"
source "$SCRIPT_DIR/scripts/server.sh"
source "$SCRIPT_DIR/scripts/convert.sh"
source "$SCRIPT_DIR/scripts/menu.sh"

menu