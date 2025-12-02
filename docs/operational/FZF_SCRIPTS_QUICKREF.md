# fzf Scripts - Quick Reference

## Overview
Four unified scripts providing system-wide and project-level fzf functionality.

## Scripts at a Glance

| Script | Purpose | Size | Usage |
|--------|---------|------|-------|
| `lib_fzf_setup.sh` | Shared library | 341 lines | Source in other scripts |
| `setup_system_fzf.sh` | System fzf setup | 68 lines | Run once: `./setup_system_fzf.sh` |
| `setup_project_fzf.sh` | Project launcher setup | 185 lines | Run per project: `./setup_project_fzf.sh` |
| `run_project_cmds.sh` | Project command launcher | 14 lines | Run often: `./run_project_cmds.sh` |

## Quick Start

### 1. System-Wide Setup (one-time)
```bash
cd /path/to/scripts
./setup_system_fzf.sh
```

**What it does:**
- Installs fzf if needed (supports apt, brew, pacman, dnf, zypper, apk, git)
- Detects your shell (bash/zsh)
- Adds fzf integration to shell config
- Enables key bindings: CTRL-T, CTRL-R, ALT-C

**Next step:** Reload your shell
```bash
source ~/.bashrc     # or ~/.zshrc
```

### 2. Project Setup (per project)
```bash
cd /path/to/project
/path/to/scripts/setup_project_fzf.sh
```

**What it does:**
- Copies `run_project_cmds.sh` to your project
- Creates `.project_cmds.txt` file
- Asks if you want a template (recommended)
- Confirms before overwriting existing files

**Next step:** Edit `.project_cmds.txt` with your commands

### 3. Use Project Launcher
```bash
./run_project_cmds.sh
```

**What it does:**
- Finds `.project_cmds.txt` (searches parent directories)
- Shows fzf menu with all commands
- Executes selected command

## Library Functions

### Available in lib_fzf_setup.sh (15 functions)

```bash
# Output (colored, formatted)
print_info "message"          # Blue [INFO]
print_success "message"       # Green [SUCCESS]
print_warning "message"       # Yellow [WARNING]
print_error "message"         # Red [ERROR]
print_header "title"          # Header banner
print_footer                  # Footer banner

# User Input
prompt_user "question" "default_value"  # Returns user input

# Shell Detection
detect_shell                  # Returns: bash or zsh
get_shell_config_file "bash"  # Returns: ~/.bashrc

# fzf Management
check_fzf                     # Returns 0 if installed
install_fzf                   # Interactive install
validate_fzf_installation     # Exit if not found

# Shell Integration
setup_shell_integration "bash" "~/.bashrc"

# Project Launcher
run_project_command           # Find and run project command

# Utilities
safe_create_file "path" "content"
```

## Create Custom Script Using Library

```bash
#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib_fzf_setup.sh"

# Now you can use all 15 library functions
print_success "fzf is ready!"
check_fzf || install_fzf
run_project_command
```

## .project_cmds.txt Format

```bash
# Organize commands by category

# ================================
# 🚀 Development Commands
# ================================
npm install
npm run dev
npm test

# ================================
# 🐳 Docker Commands
# ================================
docker-compose up --build
docker-compose down
docker-compose logs -f

# ================================
# 📦 Deployment
# ================================
npm run build
npm run deploy
```

**Note:** Comments (lines starting with #) are ignored by fzf

## Key Features

✅ **Zero Code Duplication** - Single source of truth
✅ **Consistent UI** - Same colors and messages everywhere
✅ **Error Handling** - Clear error messages
✅ **Auto-discovery** - Finds commands in parent directories
✅ **Non-destructive** - Confirms before overwriting
✅ **Extensible** - Library functions available for custom scripts

## Common Tasks

### Check if fzf is installed
```bash
source lib_fzf_setup.sh
check_fzf && echo "Ready!" || echo "Not installed"
```

### Install fzf with color output
```bash
source lib_fzf_setup.sh
print_info "Installing fzf..."
install_fzf
```

### Create formatted output
```bash
source lib_fzf_setup.sh
print_header "My Custom Script"
print_success "Operation completed!"
print_warning "This is a warning"
print_error "This is an error" >&2
print_footer
```

### Get user input with default
```bash
source lib_fzf_setup.sh
result=$(prompt_user "Enter project name" "default-project")
echo "You chose: $result"
```

## Troubleshooting

### "fzf not found"
System-wide setup not run. Do this first:
```bash
./setup_system_fzf.sh
source ~/.bashrc  # or ~/.zshrc
```

### "No .project_cmds.txt found"
Run project setup in your project directory:
```bash
/path/to/setup_project_fzf.sh
```

### "Permission denied"
Make scripts executable:
```bash
chmod +x setup_system_fzf.sh setup_project_fzf.sh run_project_cmds.sh
```

### Library not sourcing
Ensure script is in same directory, or use absolute path:
```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib_fzf_setup.sh"
```

## File Organization

```
vanna-engine/
├── lib_fzf_setup.sh              ← Start here (shared)
├── setup_system_fzf.sh           ← Run once
├── setup_project_fzf.sh          ← Run per project
├── run_project_cmds.sh           ← Use in projects
├── FZF_SETUP_GUIDE.md            ← Full documentation
├── CONSOLIDATION_SUMMARY.md      ← Technical details
├── CONSOLIDATION_COMPLETE.md     ← Implementation notes
└── FZF_SCRIPTS_QUICKREF.md      ← This file
```

## Version Info

- **Library Version**: 1.0
- **Scripts Unified**: setup_system_fzf, setup_project_fzf, run_project_cmds
- **Functions**: 15 exported
- **Total Lines**: 608 (all files)
- **Code Duplication**: 0%

---

For detailed information, see **FZF_SETUP_GUIDE.md**
For technical details, see **CONSOLIDATION_SUMMARY.md**
