#!/usr/bin/env bash

# ----------------------------------------------------------------------
#  DAIAN – Development Environment Activator
#  Loads development-specific configuration without installing package
# ----------------------------------------------------------------------


# --- Resolve project root ---------------------------------------------------
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

DEV_CONFIG_DIR="$PROJECT_ROOT/dev_config"

# --- Safety check ------------------------------------------------------------
if [ ! -d "$DEV_CONFIG_DIR" ]; then
    echo "[ERROR] dev_config directory not found at:"
    echo "        $DEV_CONFIG_DIR"
    echo ""
    echo "Please create it and include:"
    echo "  - app_settings.yaml"
    echo "  - user_settings.yaml"
    echo ""
    exit 1
fi

# --- Export variables --------------------------------------------------------
export DAIAN_CONFIG_DIR="$DEV_CONFIG_DIR"

echo "----------------------------------------------------------------------"
echo "   DAIAN DEVELOPMENT ENVIRONMENT LOADED"
echo "----------------------------------------------------------------------"
echo "  Project Root:       $PROJECT_ROOT"
echo "  Dev Config:         $DAIAN_CONFIG_DIR"
echo "  Python venv:        $(which python 2>/dev/null)"
echo "----------------------------------------------------------------------"
echo " [>] Your config files will be loaded from dev_config/"
echo " [>] Run your CLI normally:  daian ...  or  python src/main.py"
echo "----------------------------------------------------------------------"
echo ""

# Keep environment active when sourced
return 0 2>/dev/null || exit 0
