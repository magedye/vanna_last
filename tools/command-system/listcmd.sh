#!/bin/bash
# =============================================================================
# Project Command Management System - Linux Edition
# Version: 1.0.0
# Portable - No Install - No Root - Safe & Reliable
# =============================================================================
#
# USAGE:
#   ./listcmd.sh                 # Show all commands
#   ./listcmd.sh cat build       # Show build category
#   ./listcmd.sh search keyword  # Search commands
#   ./listcmd.sh dry             # Dry run mode
#
# FEATURES:
#   - Category-based organization
#   - Numeric selection
#   - Safe execution with confirmation
#   - Clipboard support (copy mode, requires xclip)
#   - Logging all actions
#   - No system modifications
#   - Zero installation required
#
# =============================================================================

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
GRAY='\033[0;90m'
WHITE='\033[1;37m'
NC='\033[0m'

# Path configuration
BASE="$(cd "$(dirname "$0")" && pwd)"
CMD_FILE="$BASE/project_commands.txt"
LOG_FILE="$BASE/project_commands.log"
SEP="::"

# Create files if they don't exist
[ ! -f "$CMD_FILE" ] && touch "$CMD_FILE" && echo "Created $CMD_FILE - Add your commands there!"
[ ! -f "$LOG_FILE" ] && touch "$LOG_FILE"

# -----------------------------------------------------------------------------
# Logging Function
# -----------------------------------------------------------------------------
log() {
    local level="${2:-INFO}"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local os="Linux"
    echo "[$timestamp] [$os] ($USER) [$level] $1" >> "$LOG_FILE"
}

# -----------------------------------------------------------------------------
# Parse Commands File
# -----------------------------------------------------------------------------
read_cmds() {
    local group="default"
    local line_num=0
    
    while IFS= read -r line; do
        ((line_num++))
        # Trim whitespace without xargs to avoid quote issues
        local t="${line#"${line%%[![:space:]]*}"}"
        t="${t%"${t##*[![:space:]]}"}"
        
        # Skip empty lines and comments
        [[ -z "$t" || "$t" =~ ^# ]] && continue

        # Category header
        if [[ "$t" =~ ^\[(.*)\]$ ]]; then
            group="${BASH_REMATCH[1]}"
            continue
        fi

        # Parse command line - manually split by :: separator
        local cmd desc mode notes
        
        # Split on first ::
        if [[ "$t" =~ ^([^:]*)::(.*)$ ]]; then
            cmd="${BASH_REMATCH[1]}"
            local rest="${BASH_REMATCH[2]}"
            
            # Split rest on second ::
            if [[ "$rest" =~ ^([^:]*)::(.*)$ ]]; then
                desc="${BASH_REMATCH[1]}"
                rest="${BASH_REMATCH[2]}"
                
                # Split rest on third ::
                if [[ "$rest" =~ ^([^:]*)::(.*)$ ]]; then
                    mode="${BASH_REMATCH[1]}"
                    notes="${BASH_REMATCH[2]}"
                else
                    mode="$rest"
                    notes=""
                fi
            else
                desc="$rest"
                mode="exec"
                notes=""
            fi
        else
            log "Malformed command at line $line_num: $t" "WARN"
            continue
        fi
        
        # Trim each field
        cmd=$(echo "$cmd" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
        desc=$(echo "$desc" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
        mode=$(echo "$mode" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
        notes=$(echo "$notes" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
        
        echo "$group|$cmd|$desc|$mode|$notes|$line_num"
    done < "$CMD_FILE"
}

# -----------------------------------------------------------------------------
# Execute Command
# -----------------------------------------------------------------------------
exec_cmd() {
    local entry="$1"
    local dry_run="$2"
    
    IFS='|' read -r group cmd desc mode notes line_num <<< "$entry"

    if [[ "$dry_run" == "true" ]]; then
        echo -e "\n${YELLOW}[DRY RUN MODE]${NC}"
        echo -e "${CYAN}Would execute: $cmd${NC}"
        echo -e "${GRAY}Mode: $mode${NC}"
        [[ -n "$notes" ]] && echo -e "${GRAY}Note: $notes${NC}"
        return
    fi

    echo -e "\n${CYAN}========================================${NC}"
    echo -e "${CYAN}Selected Command:${NC}"
    echo -e "${WHITE}$cmd${NC}"
    echo -e "${GRAY}Description: $desc${NC}"
    echo -e "${GRAY}Mode: $mode${NC}"
    [[ -n "$notes" ]] && echo -e "${YELLOW}Note: $notes${NC}"
    echo -e "${CYAN}========================================${NC}"

    # Confirmation for exec mode
    if [[ "$mode" == "exec" ]]; then
        echo -e -n "\n${WHITE}Execute this command? (y/n): ${NC}"
        read -r confirm
        if [[ "$confirm" != "y" ]]; then
            echo -e "${YELLOW}Cancelled.${NC}"
            log "Cancelled: $cmd" "INFO"
            return
        fi
    fi

    case "$mode" in
        copy)
            if command -v xclip &> /dev/null; then
                printf "%s" "$cmd" | xclip -selection clipboard
                echo -e "\n${GREEN}✓ Copied to clipboard.${NC}"
                log "Copied: $cmd" "INFO"
            elif command -v pbcopy &> /dev/null; then
                printf "%s" "$cmd" | pbcopy
                echo -e "\n${GREEN}✓ Copied to clipboard (pbcopy).${NC}"
                log "Copied: $cmd" "INFO"
            else
                echo -e "\n${YELLOW}⚠ Clipboard utility not found (install xclip).${NC}"
                echo -e "${GRAY}Command: $cmd${NC}"
                log "Copy attempted but no clipboard utility: $cmd" "WARN"
            fi
            ;;
        show)
            echo -e "\n${GREEN}$cmd${NC}"
            log "Shown: $cmd" "INFO"
            ;;
        exec|*)
            echo -e "\n${CYAN}Executing...${NC}"
            if eval "$cmd"; then
                local exit_code=$?
                echo -e "\n${GREEN}✓ Command completed (Exit code: $exit_code)${NC}"
                log "Executed: $cmd [Exit: $exit_code]" "INFO"
            else
                local exit_code=$?
                echo -e "\n${RED}✗ Command failed (Exit code: $exit_code)${NC}"
                log "Failed: $cmd [Exit: $exit_code]" "ERROR"
            fi
            ;;
    esac
}

# -----------------------------------------------------------------------------
# Display Menu
# -----------------------------------------------------------------------------
show_menu() {
    local -a entries=("$@")
    
    if [[ ${#entries[@]} -eq 0 ]]; then
        echo -e "\n${YELLOW}No commands found.${NC}"
        return 1
    fi

    echo -e "\n${CYAN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║              PROJECT COMMAND MANAGEMENT SYSTEM                       ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    local current_group=""
    local i=1
    
    for entry in "${entries[@]}"; do
        IFS='|' read -r group cmd desc mode notes line_num <<< "$entry"
        
        # Print category header when group changes
        if [[ "$group" != "$current_group" ]]; then
            echo -e "\n${YELLOW}[${group^^}]${NC}"
            current_group="$group"
        fi
        
        # Color code by mode
        local cmd_color="$WHITE"
        case "$mode" in
            exec) cmd_color="$GREEN" ;;
            copy) cmd_color="$CYAN" ;;
            show) cmd_color="$MAGENTA" ;;
        esac
        
        echo -e "  ${WHITE}[$i]${NC} ${cmd_color}$cmd${NC} ${GRAY}— $desc${NC}"
        ((i++))
    done

    echo ""
    echo -e -n "${WHITE}Enter number (or 'q' to quit): ${NC}"
    read -r sel
    
    if [[ "$sel" == "q" ]]; then
        echo -e "${CYAN}Goodbye!${NC}"
        return 1
    fi
    
    if [[ "$sel" =~ ^[0-9]+$ ]] && [[ $sel -ge 1 ]] && [[ $sel -le ${#entries[@]} ]]; then
        echo "${entries[$((sel-1))]}"
        return 0
    else
        echo -e "${RED}Invalid selection.${NC}"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# Main Function
# -----------------------------------------------------------------------------
listcmd() {
    local action="$1"
    local param="$2"
    local dry_run="false"
    
    log "Started - Action: $action, Filter: $param" "INFO"

    # Read all commands
    mapfile -t all_entries < <(read_cmds)
    
    if [[ ${#all_entries[@]} -eq 0 ]]; then
        echo -e "\n${YELLOW}No commands found in $CMD_FILE${NC}"
        echo -e "${GRAY}Add commands in the format: command :: description :: mode${NC}"
        return
    fi

    local -a entries=("${all_entries[@]}")

    # Apply filters based on action
    case "$action" in
        search)
            # Search mode
            local -a filtered=()
            for entry in "${all_entries[@]}"; do
                if echo "$entry" | grep -qi "$param"; then
                    filtered+=("$entry")
                fi
            done
            entries=("${filtered[@]}")
            
            if [[ ${#entries[@]} -eq 0 ]]; then
                echo -e "\n${YELLOW}No matches found for: $param${NC}"
                return
            fi
            echo -e "\n${GREEN}Found ${#entries[@]} match(es) for: $param${NC}"
            ;;
        cat)
            # Category filter
            local -a filtered=()
            for entry in "${all_entries[@]}"; do
                IFS='|' read -r group _ <<< "$entry"
                if [[ "$group" == "$param" ]]; then
                    filtered+=("$entry")
                fi
            done
            entries=("${filtered[@]}")
            
            if [[ ${#entries[@]} -eq 0 ]]; then
                echo -e "\n${YELLOW}No commands in category: $param${NC}"
                return
            fi
            ;;
        dry)
            dry_run="true"
            ;;
    esac

    # Show menu and get selection
    local selected
    selected=$(show_menu "${entries[@]}")
    
    if [[ $? -eq 0 && -n "$selected" ]]; then
        exec_cmd "$selected" "$dry_run"
    fi
}

# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------
echo ""
echo -e "${CYAN}Vanna Insight Engine - Command System v1.0.0${NC}"
echo -e "${GRAY}OS: Linux | User: $USER${NC}"
echo ""

case "$1" in
    search)
        listcmd "search" "$2"
        ;;
    cat)
        listcmd "cat" "$2"
        ;;
    dry)
        listcmd "dry" "$2"
        ;;
    "")
        listcmd "" ""
        ;;
    *)
        echo -e "${RED}Unknown action: $1${NC}"
        echo -e "${GRAY}Valid actions: search, cat, dry${NC}"
        ;;
esac

echo ""
