# Publishing Guide for AnyTask CLI

This guide covers how to publish and distribute the `anyt` CLI tool.

## Prerequisites

1. **PyPI Account**: Sign up at [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. **TestPyPI Account** (for testing): Sign up at [https://test.pypi.org/account/register/](https://test.pypi.org/account/register/)
3. **API Tokens**: Generate tokens for authentication
   - PyPI: [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
   - TestPyPI: [https://test.pypi.org/manage/account/token/](https://test.pypi.org/manage/account/token/)

## Method 1: Publish to PyPI (Recommended for Public Distribution)

### Step 1: Update Version Number

Edit `pyproject.toml` and `src/cli/__init__.py`:

```python
# src/cli/__init__.py
__version__ = "0.1.1"  # Increment version
```

```toml
# pyproject.toml
[project]
version = "0.1.1"  # Must match __init__.py
```

### Step 2: Build Distribution Packages

```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build wheel and source distribution
uv build
# or
python -m build

# This creates:
# - dist/anyt-0.1.1-py3-none-any.whl
# - dist/anyt-0.1.1.tar.gz
```

### Step 3: Test on TestPyPI First

```bash
# Upload to TestPyPI
uv run twine upload --repository testpypi dist/*
# or
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ anyt
anyt --version
```

### Step 4: Publish to PyPI

```bash
# Upload to PyPI
uv run twine upload dist/*
# or
python -m twine upload dist/*

# When prompted, use your API token:
# Username: __token__
# Password: pypi-...your-token...
```

### Step 5: Users Can Install

Once published, anyone can install with:

```bash
# Install the latest version
pip install anyt

# Install specific version
pip install anyt==0.1.1

# Install with pipx (recommended for CLI tools)
pipx install anyt

# Verify installation
anyt --version
anyt --help
```

## Method 2: GitHub Releases (For Binary Distribution)

### Option A: Wheel Distribution

```bash
# Build wheel
uv build

# Create GitHub release and attach:
# - dist/anyt-0.1.1-py3-none-any.whl
# - dist/anyt-0.1.1.tar.gz
```

Users install from GitHub:
```bash
pip install https://github.com/yourusername/AnyTaskBackend/releases/download/v0.1.1/anyt-0.1.1-py3-none-any.whl
```

### Option B: Using PyInstaller (Single Executable)

Create standalone executables for different platforms:

```bash
# Install PyInstaller
uv add --dev pyinstaller

# Create executable
uv run pyinstaller --onefile --name anyt src/cli/main.py

# This creates:
# - dist/anyt (macOS/Linux)
# - dist/anyt.exe (Windows)
```

Users can download and run directly without Python installed!

## Method 3: Docker Image Distribution

```dockerfile
# Dockerfile.cli
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install -e .

ENTRYPOINT ["anyt"]
```

Build and publish:
```bash
# Build image
docker build -f Dockerfile.cli -t yourusername/anyt:0.1.1 .

# Push to Docker Hub
docker push yourusername/anyt:0.1.1

# Tag as latest
docker tag yourusername/anyt:0.1.1 yourusername/anyt:latest
docker push yourusername/anyt:latest
```

Users run with Docker:
```bash
docker run -it yourusername/anyt:latest --help
```

## Method 4: Direct Installation from Git

Users can install directly from your GitHub repository:

```bash
# Install from main branch
pip install git+https://github.com/yourusername/AnyTaskBackend.git

# Install from specific branch/tag
pip install git+https://github.com/yourusername/AnyTaskBackend.git@v0.1.1

# Install in editable mode for development
pip install -e git+https://github.com/yourusername/AnyTaskBackend.git#egg=anyt
```

## Method 5: Homebrew (macOS/Linux)

Create a Homebrew formula for easy installation on macOS:

1. Create a tap repository: `homebrew-anyt`
2. Create formula: `Formula/anyt.rb`

```ruby
class Anyt < Formula
  include Language::Python::Virtualenv

  desc "AI-native task management CLI"
  homepage "https://github.com/yourusername/AnyTaskBackend"
  url "https://github.com/yourusername/AnyTaskBackend/archive/v0.1.1.tar.gz"
  sha256 "..." # Calculate with: shasum -a 256 v0.1.1.tar.gz
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/anyt", "--version"
  end
end
```

Users install with:
```bash
brew tap yourusername/anyt
brew install anyt
```

## Method 6: Using `pipx` (Recommended for CLI Tools)

`pipx` is the recommended way to install Python CLI applications:

### For Publishers:
Just publish to PyPI as normal. `pipx` handles the rest.

### For Users:
```bash
# Install pipx
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install anyt in isolated environment
pipx install anyt

# Upgrade
pipx upgrade anyt

# Uninstall
pipx uninstall anyt
```

Benefits:
- Isolated environment (no dependency conflicts)
- CLI available globally
- Easy updates and management

## Best Practices

### 1. Semantic Versioning

Use semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### 2. Changelog

Maintain a `CHANGELOG.md`:

```markdown
# Changelog

## [0.1.1] - 2025-01-15
### Added
- New `anyt graph` command for dependency visualization

### Fixed
- Fixed authentication token refresh issue

## [0.1.0] - 2025-01-01
### Added
- Initial release
```

### 3. Git Tags

Tag releases in Git:

```bash
git tag -a v0.1.1 -m "Release version 0.1.1"
git push origin v0.1.1
```

### 4. CI/CD Automation

Automate publishing with GitHub Actions:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install build twine
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: twine upload dist/*
```

### 5. Version Management

Keep versions in sync:

```bash
# Update version in both files
# 1. src/cli/__init__.py
# 2. pyproject.toml

# Or use bump2version
pip install bump2version
bump2version patch  # 0.1.0 -> 0.1.1
```

## Quick Publishing Checklist

- [ ] Update version in `pyproject.toml` and `src/cli/__init__.py`
- [ ] Update `CHANGELOG.md`
- [ ] Update documentation if needed
- [ ] Run tests: `make test`
- [ ] Run linters: `make lint format typecheck`
- [ ] Build package: `uv build`
- [ ] Test on TestPyPI
- [ ] Publish to PyPI: `twine upload dist/*`
- [ ] Create Git tag: `git tag v0.1.1`
- [ ] Push tag: `git push origin v0.1.1`
- [ ] Create GitHub Release with notes
- [ ] Test installation: `pip install anyt`

## Installation Commands Summary

For different user types:

```bash
# Regular users (PyPI)
pip install anyt
# or
pipx install anyt

# From source/development
pip install -e .
# or
uv pip install -e .

# From GitHub
pip install git+https://github.com/yourusername/AnyTaskBackend.git

# From local wheel
pip install anyt-0.1.1-py3-none-any.whl

# From Docker
docker run -it yourusername/anyt:latest

# From Homebrew (if you create a tap)
brew install yourusername/anyt/anyt
```

## Support & Documentation

- Include installation instructions in `README.md`
- Create user documentation in `docs/`
- Provide troubleshooting guide
- Set up issue templates on GitHub

