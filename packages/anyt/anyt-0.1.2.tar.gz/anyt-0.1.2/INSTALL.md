# Installation Guide for AnyTask CLI

## For End Users (Simple Installation)

### Method 1: Install from PyPI (Once Published)

The easiest way to install `anyt` CLI:

```bash
# Using pip
pip install anyt

# Using pipx (recommended for CLI tools)
pipx install anyt

# Verify installation
anyt --help
```

### Method 2: Install from GitHub

Install directly from the repository:

```bash
# Latest version from main branch
pip install git+https://github.com/yourusername/AnyTaskBackend.git

# Specific version/tag
pip install git+https://github.com/yourusername/AnyTaskBackend.git@v0.1.0

# With pipx
pipx install git+https://github.com/yourusername/AnyTaskBackend.git
```

### Method 3: Install from Wheel (Downloaded Release)

Download the `.whl` file from GitHub Releases and install:

```bash
pip install anyt-0.1.0-py3-none-any.whl
```

## For Developers (Development Setup)

### Prerequisites
- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)
- Git

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/AnyTaskBackend.git
cd AnyTaskBackend
```

### Step 2: Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e ".[dev]"
```

### Step 3: Run the CLI

```bash
# With uv
uv run anyt --help

# With activated virtual environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows
anyt --help
```

### Step 4: Run Tests

```bash
# All tests
make test

# Linting
make lint

# Type checking
make typecheck
```

## Platform-Specific Instructions

### macOS

```bash
# Install pipx if not already installed
brew install pipx
pipx ensurepath

# Install anyt
pipx install anyt

# Or from source
git clone https://github.com/yourusername/AnyTaskBackend.git
cd AnyTaskBackend
make install
```

### Linux

```bash
# Install pipx
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install anyt
pipx install anyt
```

### Windows

```powershell
# Install pipx
python -m pip install --user pipx
python -m pipx ensurepath

# Install anyt
pipx install anyt
```

## Docker Installation

Run anyt in Docker without installing Python:

```bash
# Pull image
docker pull yourusername/anyt:latest

# Run commands
docker run -it yourusername/anyt:latest --help

# Create alias for convenience
alias anyt="docker run -it -v $(pwd):/workspace yourusername/anyt:latest"
```

## Updating

### pip/pipx

```bash
# With pip
pip install --upgrade anyt

# With pipx
pipx upgrade anyt
```

### From source

```bash
cd AnyTaskBackend
git pull origin main
uv sync
```

## Uninstalling

```bash
# With pip
pip uninstall anyt

# With pipx
pipx uninstall anyt
```

## Troubleshooting

### Command not found: anyt

**Problem**: After installation, `anyt` command is not found.

**Solutions**:

1. **Using pipx**: Ensure pipx path is in your PATH
   ```bash
   pipx ensurepath
   source ~/.bashrc  # or ~/.zshrc
   ```

2. **Using pip**: Check if Python scripts directory is in PATH
   ```bash
   # Find the installation location
   pip show anyt
   
   # Add to PATH (Linux/macOS)
   export PATH="$HOME/.local/bin:$PATH"
   
   # Add to PATH (Windows)
   # Add %USERPROFILE%\AppData\Local\Programs\Python\Python312\Scripts to PATH
   ```

3. **Using virtual environment**: Activate it first
   ```bash
   source .venv/bin/activate
   anyt --help
   ```

4. **Use full path**:
   ```bash
   python -m cli.main --help
   ```

### Permission denied error

**Problem**: Permission denied when installing with pip.

**Solution**: Use `--user` flag or pipx:
```bash
pip install --user anyt
# or
pipx install anyt
```

### ImportError or ModuleNotFoundError

**Problem**: Missing dependencies.

**Solution**: Reinstall with all dependencies:
```bash
pip install --force-reinstall anyt
```

### Python version incompatible

**Problem**: Requires Python 3.12+

**Solution**: Install Python 3.12 or use pyenv:
```bash
# Install pyenv
curl https://pyenv.run | bash

# Install Python 3.12
pyenv install 3.12.0
pyenv global 3.12.0

# Reinstall anyt
pip install anyt
```

## Verifying Installation

After installation, verify everything works:

```bash
# Check version
anyt --help

# Check available commands
anyt env --help
anyt auth --help
anyt task --help

# Quick test
anyt env add local http://localhost:8000
```

## Getting Started

After installation, see the [CLI Usage Guide](docs/CLI_USAGE.md) for complete documentation.

Quick start:

```bash
# Add server endpoint
anyt env add dev http://localhost:8000

# Login
anyt auth login --agent-key your_key_here

# Initialize workspace
anyt workspace init

# Create a task
anyt task add "My first task"

# View tasks
anyt board
```

## Support

- **Documentation**: [docs/CLI_USAGE.md](docs/CLI_USAGE.md)
- **Issues**: https://github.com/yourusername/AnyTaskBackend/issues
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

