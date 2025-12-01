#!/bin/bash
# ============================================================================
# Project Command System Launcher - Linux/macOS
# ============================================================================
# Usage:
#   ./run_listcmd.sh              - Show all commands
#   ./run_listcmd.sh cat build    - Show build category
#   ./run_listcmd.sh search test  - Search for 'test'
#   ./run_listcmd.sh dry          - Dry run mode
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASH_SCRIPT="$SCRIPT_DIR/listcmd.sh"

if [ ! -f "$BASH_SCRIPT" ]; then
    echo "Error: listcmd.sh not found in $SCRIPT_DIR"
    exit 1
fi

# Make sure it's executable
chmod +x "$BASH_SCRIPT"

# Execute with all arguments
bash "$BASH_SCRIPT" "$@"
