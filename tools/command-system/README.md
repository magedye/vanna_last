# Project Command Management System

**Version:** 1.0.0  
**Status:** Production Ready  
**Platform:** Windows & Linux

---

## Overview

A portable, zero-installation, cross-platform command launcher that helps developers quickly discover and execute project commands. No admin rights required, no system modifications, runs entirely within the project folder.

---

## Features

✅ **Cross-Platform** - Identical behavior on Windows and Linux  
✅ **Zero Installation** - No dependencies, no setup  
✅ **Category Organization** - Commands grouped logically  
✅ **Three Execution Modes**:
- `exec` - Execute the command
- `copy` - Copy to clipboard
- `show` - Display only (no execution)

✅ **Safety** - Confirmation before execution  
✅ **Search** - Find commands by keyword  
✅ **Filtering** - Show specific categories  
✅ **Dry Run** - Preview without executing  
✅ **Logging** - All actions logged  
✅ **Error Handling** - Graceful failures

---

## Quick Start

### Windows

```cmd
cd tools\command-system
run_listcmd.cmd
```

### Linux/macOS

```bash
cd tools/command-system
./run_listcmd.sh
```

---

## Usage

### Show All Commands

```bash
# Windows
run_listcmd.cmd

# Linux
./run_listcmd.sh
```

### Filter by Category

```bash
# Show only build commands
run_listcmd.cmd cat build

# Show only test commands
./run_listcmd.sh cat test
```

### Search Commands

```bash
# Search for 'docker' in all fields
run_listcmd.cmd search docker

# Search for 'test'
./run_listcmd.sh search test
```

### Dry Run Mode

```bash
# See what would execute without running
run_listcmd.cmd dry

./run_listcmd.sh dry
```

---

## Command File Format

Commands are stored in `project_commands.txt`:

```
[category]
command :: description :: mode :: notes (optional)
```

### Example

```
[build]
npm install :: Install dependencies :: exec
npm run build :: Build project :: exec :: Production build

[test]
npm test :: Run tests :: exec
npm run coverage :: Generate coverage :: exec

[info]
cat README.md :: Show README :: show
```

### Fields

| Field | Required | Description | Default |
|-------|----------|-------------|---------|
| command | ✅ Yes | The actual command to execute | - |
| description | ✅ Yes | Human-readable description | - |
| mode | ⚠️ Optional | `exec`, `copy`, or `show` | `exec` |
| notes | ⚠️ Optional | Additional context/warnings | - |

---

## Execution Modes

### exec (Execute)

Runs the command and shows output. Requires confirmation.

```
docker compose up -d :: Start services :: exec
```

### copy (Copy to Clipboard)

Copies command to clipboard without executing.

```
kubectl apply -k k8s/prod :: Deploy to production :: copy
```

Use `copy` for:
- Commands requiring manual editing
- Multi-step workflows
- Destructive operations

### show (Display Only)

Prints the command without execution.

```
echo "Current directory" :: Show message :: show
```

Use `show` for:
- Information display
- Documentation
- URL references

---

## Categories

Organize commands into logical groups:

### Built-in Categories

- `[environment]` - Environment setup
- `[install]` - Dependency installation
- `[database]` - Database operations
- `[build]` - Build processes
- `[run]` - Start services
- `[test]` - Testing commands
- `[docker]` - Docker operations
- `[monitor]` - Monitoring & health
- `[api]` - API testing
- `[cleanup]` - Clean operations
- `[deploy]` - Deployment
- `[dev]` - Development tools
- `[info]` - Information & docs
- `[troubleshoot]` - Debugging

---

## Safety Features

### Confirmation Prompts

All `exec` commands require confirmation:

```
Selected Command:
docker compose down -v

Execute this command? (y/n):
```

### Dry Run

Preview commands without executing:

```bash
./run_listcmd.sh dry
```

Shows:
```
[DRY RUN MODE]
Would execute: docker compose up -d
Mode: exec
```

### Logging

All actions logged to `project_commands.log`:

```
[2025-11-17 23:45:12] [Linux] (user) [INFO] Executed: docker compose ps [Exit: 0]
[2025-11-17 23:46:03] [INFO] Cancelled: docker compose down -v
[2025-11-17 23:47:21] [INFO] Copied: kubectl apply -k k8s/prod
```

---

## Adding New Commands

1. **Edit** `project_commands.txt`
2. **Add** command in format: `command :: description :: mode`
3. **Save** the file
4. **Run** `run_listcmd` - new commands appear immediately

### Example

```
[deploy]
./deploy.sh staging :: Deploy to staging :: exec
./deploy.sh production :: Deploy to production :: exec :: ⚠️ PRODUCTION
```

---

## Advanced Usage

### Clipboard Support

#### Windows
Built-in `Set-Clipboard` (no dependencies)

#### Linux
Requires `xclip` or `pbcopy`:

```bash
# Install xclip (Ubuntu/Debian)
sudo apt-get install xclip

# Install xclip (Fedora/RHEL)
sudo dnf install xclip
```

If unavailable, command is displayed instead of copied.

### Multi-line Commands

For complex commands, use semicolons or `&&`:

```
cd vanna-engine && ./run.sh --env prod :: Start production :: exec
```

### Environment Variables

Commands inherit environment from parent shell:

```
echo $PATH :: Show PATH :: show
echo $USER :: Show current user :: show
```

---

## File Structure

```
tools/command-system/
├── README.md                  # This file
├── project_commands.txt       # Command definitions
├── project_commands.log       # Execution log
├── listcmd.ps1                # Windows PowerShell engine
├── listcmd.sh                 # Linux Bash engine
├── run_listcmd.cmd            # Windows launcher
└── run_listcmd.sh             # Linux launcher
```

---

## Troubleshooting

### "Command not found" on Linux

Make scripts executable:

```bash
chmod +x run_listcmd.sh listcmd.sh
```

### PowerShell Execution Policy Error

Run with bypass:

```cmd
powershell -ExecutionPolicy Bypass -File listcmd.ps1
```

Or use the launcher:

```cmd
run_listcmd.cmd
```

### Clipboard Not Working (Linux)

Install `xclip`:

```bash
sudo apt-get install xclip
```

### Commands Not Showing

Check `project_commands.txt` format:

```
command :: description :: mode
```

Ensure:
- No missing `::`
- No extra colons in command
- Categories are `[lowercase]`

### Log File Growing Large

Truncate log file:

```bash
# Keep last 1000 lines
tail -1000 project_commands.log > temp.log && mv temp.log project_commands.log
```

---

## Integration with CI/CD

### GitHub Actions

```yaml
- name: List available commands
  run: |
    cd tools/command-system
    ./run_listcmd.sh search test
```

### GitLab CI

```yaml
script:
  - cd tools/command-system
  - ./run_listcmd.sh cat deploy
```

---

## Best Practices

### 1. Use Descriptive Names

❌ Bad: `npm test :: test :: exec`  
✅ Good: `npm test :: Run unit tests :: exec`

### 2. Add Notes for Warnings

```
docker compose down -v :: Remove all data :: exec :: ⚠️ DATA LOSS WARNING
```

### 3. Use `copy` for Destructive Commands

```
rm -rf node_modules :: Delete dependencies :: copy :: Requires confirmation
```

### 4. Group Related Commands

```
[database]
alembic upgrade head :: Apply migrations :: exec
alembic downgrade -1 :: Rollback last migration :: exec
```

### 5. Include Environment Context

```
./run.sh --env prod :: Start production server :: exec :: Uses .env.prod
```

---

## Security Considerations

✅ **No Elevated Privileges** - Runs with user permissions  
✅ **Confirmation Required** - All executions confirmed  
✅ **Logging** - Full audit trail  
✅ **No System Modifications** - Stays in project folder  
✅ **Version Controlled** - Commands tracked in git

⚠️ **Warnings**:
- Commands execute with your user permissions
- Avoid storing secrets in commands
- Use environment variables for sensitive data

---

## Changelog

### Version 1.0.0 (2025-11-17)

- ✨ Initial release
- ✅ Cross-platform support (Windows/Linux)
- ✅ Category filtering
- ✅ Search functionality
- ✅ Dry run mode
- ✅ Three execution modes (exec, copy, show)
- ✅ Comprehensive logging
- ✅ Color-coded output
- ✅ Safety confirmations

---

## License

Same as parent project.

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review `project_commands.log` for errors
3. Verify command syntax in `project_commands.txt`
4. Consult project documentation

---

**Maintained by:** Vanna Insight Engine Team  
**Last Updated:** November 17, 2025  
**Version:** 1.0.0
