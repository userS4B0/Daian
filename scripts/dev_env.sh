#!/usr/bin/env bash

# ----------------------------------------------------------------------
#  DAIAN – Development Environment Activator
#  Loads development-specific configuration without installing package
# ----------------------------------------------------------------------

# --- Resolve project root safely -----------------------------------------
# FIXME: realpath: '': File or directory does not exist
# Minor issue with devel script, it's still works
# assignees: userS4B0
# labels: priority_low, devel, bug
# milestone: v1.0.0

SCRIPT_PATH="$(realpath "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEV_CONFIG_DIR="$PROJECT_ROOT/dev_config"

# --- Safety check --------------------------------------------------------
if [ ! -d "$DEV_CONFIG_DIR" ]; then
    echo "----------------------------------------------------------------------"
    echo "[ERROR] dev_config directory not found at:"
    echo "        $DEV_CONFIG_DIR"
    echo ""
    echo "Please create it and include:"
    echo "  - app_settings.yaml"
    echo "  - user_settings.yaml"
    echo "----------------------------------------------------------------------"
else
    export DAIAN_CONFIG_DIR="$DEV_CONFIG_DIR"
    echo "----------------------------------------------------------------------"
    echo "   DAIAN DEVELOPMENT ENVIRONMENT LOADED"
    echo "----------------------------------------------------------------------"
    echo "  Project Root:       $PROJECT_ROOT"
    echo "  Dev Config Dir:     $DAIAN_CONFIG_DIR"
    echo "  Python venv:        $(which python 2>/dev/null)"
    echo "----------------------------------------------------------------------"
    echo " [>] Your config files will be loaded from dev_config/"
    echo " [>] Run your CLI normally:  daian ...  or  python src/main.py"
    echo "----------------------------------------------------------------------"
fi

# --- Notes ---------------------------------------------------------------
# Safe to source in IDEs or terminals
# Always use:
#   source scripts/dev_env.sh
# No exit/return statements are used.
