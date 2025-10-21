#!/bin/bash
# Install anyt CLI locally for testing

set -e

echo "🔧 Installing anyt CLI locally"
echo "=============================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Must run from project root directory"
    exit 1
fi

# Get version
VERSION=$(grep 'version = ' pyproject.toml | head -1 | cut -d'"' -f2)
echo "Version: $VERSION"

# Ask installation method
echo ""
echo "Installation method:"
echo "  1) Development mode (editable, uses uv)"
echo "  2) Build and install wheel"
echo "  3) Install with pipx (recommended for CLI)"
read -p "Choose (1/2/3): " choice

case $choice in
    1)
        echo "Installing in development mode..."
        uv pip install -e .
        echo ""
        echo "✅ Installed in development mode!"
        echo "Use: uv run anyt --help"
        ;;
    2)
        echo "Building and installing wheel..."
        rm -rf dist/ build/ *.egg-info
        uv build
        pip install --force-reinstall dist/anyt-$VERSION-py3-none-any.whl
        echo ""
        echo "✅ Installed from wheel!"
        echo "Use: anyt --help"
        ;;
    3)
        echo "Installing with pipx..."
        rm -rf dist/ build/ *.egg-info
        uv build
        pipx install --force dist/anyt-$VERSION-py3-none-any.whl
        echo ""
        echo "✅ Installed with pipx!"
        echo "Use: anyt --help"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Test installation
echo ""
echo "Testing installation..."
if command -v anyt &> /dev/null; then
    anyt --version
    echo ""
    echo "🎉 Success! anyt CLI is ready to use."
else
    echo "⚠️  Command 'anyt' not found in PATH"
    echo "If you used method 1, run: source .venv/bin/activate"
    echo "Or use: uv run anyt --help"
fi

