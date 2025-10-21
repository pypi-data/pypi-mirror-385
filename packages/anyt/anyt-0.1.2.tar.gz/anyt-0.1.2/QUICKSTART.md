# AnyTask CLI - Quick Start Guide

## 🚀 5-Minute Setup

### 1. Install (Choose One Method)

```bash
# From PyPI (recommended)
pipx install anyt

# From GitHub (latest version)
pipx install git+https://github.com/yourusername/AnyTaskBackend.git

# For development
git clone https://github.com/yourusername/AnyTaskBackend.git
cd AnyTaskBackend
make install
uv run anyt --help
```

### 2. Configure Environment

```bash
# Add your backend server
anyt env add dev http://localhost:8000

# Verify
anyt env list
```

### 3. Authenticate

```bash
# Using agent key (for automation/CI)
export ANYT_AGENT_KEY=anyt_agent_your_key_here
anyt auth login

# Or using user token (interactive)
anyt auth login --token

# Verify
anyt auth whoami
```

### 4. Initialize Workspace

```bash
# In your project directory
cd /path/to/your/project
anyt workspace init

# Set workspace description
anyt workspace describe "My awesome project"
```

### 5. Start Using!

```bash
# Create your first task
anyt task add "Build authentication system" --priority 1

# View all tasks
anyt board

# Pick a task to work on
anyt task pick DEV-1

# Check active task
anyt active

# Mark as done when finished
anyt task done
```

## 📋 Common Commands

### Task Management

```bash
# Create tasks
anyt task add "Task title"
anyt task add "High priority task" --priority 1 --label bug

# List tasks
anyt task list
anyt task list --status todo --priority 1
anyt task list --label bug

# View task details
anyt task show DEV-123

# Update tasks
anyt task update DEV-123 --status in_progress
anyt task update DEV-123 --priority 2
anyt task update DEV-123 --title "New title"

# Delete tasks
anyt task delete DEV-123
```

### Workflow

```bash
# Pick a task to work on (sets as active)
anyt task pick DEV-123

# View active task
anyt active

# Mark active task as done
anyt task done

# Unpick (clear active task)
anyt task unpick
```

### Visualization

```bash
# Kanban board
anyt board

# Timeline view
anyt timeline

# Workspace summary
anyt summary

# Dependency graph
anyt graph DEV-123
```

### Dependencies

```bash
# Add dependency (DEV-456 blocks DEV-123)
anyt dep add DEV-123 --blocks DEV-456

# List dependencies
anyt dep list DEV-123

# Remove dependency
anyt dep remove DEV-123 DEV-456
```

### AI Features

```bash
# Decompose a goal into tasks
anyt ai decompose "Build user authentication system"

# Generate workspace summary
anyt ai summary --period weekly
```

### Configuration

```bash
# Manage environments
anyt env add prod https://api.anytask.dev
anyt env list
anyt env switch prod
anyt env remove dev

# Check authentication
anyt auth whoami
anyt auth status

# Logout
anyt auth logout
```

## 🎯 Typical Workflow

### Daily Development

```bash
# Morning: Check what's next
anyt board
anyt summary

# Pick a task
anyt task pick DEV-42

# Work on it...

# Evening: Mark as done
anyt task done

# Check progress
anyt timeline --limit 10
```

### Starting a New Feature

```bash
# Create task
anyt task add "Implement payment gateway" --priority 1 --label feature

# Pick it
anyt task pick DEV-100

# Break it down with AI
anyt ai decompose "Implement payment gateway"

# View all subtasks
anyt task list --parent DEV-100
```

### Managing Blocked Tasks

```bash
# View board to see blocked tasks
anyt board

# Add blocking dependency
anyt dep add DEV-101 --blocks DEV-102

# When blocker is done, check what's unblocked
anyt task update DEV-101 --status done
anyt summary
```

## 🔧 Tips & Tricks

### 1. Use Aliases

Add to `~/.bashrc` or `~/.zshrc`:

```bash
alias ab='anyt board'
alias at='anyt task'
alias aa='anyt active'
alias ap='anyt task pick'
alias ad='anyt task done'
```

### 2. Environment Variables

```bash
# Set default environment
export ANYT_ENV=production

# Set agent key for CI/CD
export ANYT_AGENT_KEY=anyt_agent_...

# Set custom config directory
export ANYT_CONFIG_DIR=~/.config/anyt
```

### 3. Tab Completion

```bash
# Install completion
anyt --install-completion

# Restart shell
source ~/.bashrc  # or ~/.zshrc
```

### 4. JSON Output for Scripting

```bash
# Get tasks as JSON
anyt task list --output json | jq '.[] | select(.status == "todo")'

# Parse with Python
anyt task show DEV-123 --output json | python -c "import sys, json; print(json.load(sys.stdin)['title'])"
```

### 5. Batch Operations

```bash
# Update multiple tasks
for id in DEV-{1..10}; do
  anyt task update $id --label refactor
done

# Create tasks from file
while read line; do
  anyt task add "$line"
done < tasks.txt
```

## 🐛 Troubleshooting

### Command not found: anyt

```bash
# Ensure pipx path is in PATH
pipx ensurepath
source ~/.bashrc

# Or use full path
~/.local/bin/anyt --help
```

### Authentication failed

```bash
# Check credentials
anyt auth whoami

# Re-login
anyt auth logout
anyt auth login --agent-key $ANYT_AGENT_KEY

# Verify server is reachable
curl http://localhost:8000/health
```

### Not in a workspace directory

```bash
# Check current workspace
ls -la .anyt/

# Initialize if needed
anyt workspace init

# Or cd to workspace root
cd /path/to/workspace/root
```

## 📚 Next Steps

- **Full Documentation**: See [docs/CLI_USAGE.md](docs/CLI_USAGE.md)
- **API Reference**: See [docs/server_api.md](docs/server_api.md)
- **Examples**: See [examples/](examples/)
- **Issues**: https://github.com/yourusername/AnyTaskBackend/issues

## 🤝 Getting Help

```bash
# Command help
anyt --help
anyt task --help
anyt task add --help

# Show version
anyt --version

# Check authentication
anyt auth status

# Verify connection
anyt env list
```

Happy task managing! 🎉

