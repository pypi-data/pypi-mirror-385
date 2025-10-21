#!/bin/bash
# Quick publish script for anyt CLI

set -e

echo "🚀 AnyTask CLI Publishing Script"
echo "================================"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get current version
VERSION=$(grep 'version = ' pyproject.toml | head -1 | cut -d'"' -f2)
echo -e "${GREEN}Current version: $VERSION${NC}"

# Check if version matches in __init__.py
INIT_VERSION=$(grep '__version__ = ' src/cli/__init__.py | cut -d'"' -f2)
if [ "$VERSION" != "$INIT_VERSION" ]; then
    echo -e "${RED}ERROR: Version mismatch!${NC}"
    echo "  pyproject.toml: $VERSION"
    echo "  cli/__init__.py: $INIT_VERSION"
    exit 1
fi

echo ""
echo "Pre-flight checks..."

# Run tests
echo -e "${YELLOW}Running tests...${NC}"
uv run pytest --ignore=tests/integration -q || {
    echo -e "${RED}Tests failed! Fix errors before publishing.${NC}"
    exit 1
}

# Run linter
echo -e "${YELLOW}Running linter...${NC}"
uv run ruff check . || {
    echo -e "${YELLOW}Linter warnings detected. Continue? (y/n)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
}

# Clean old builds
echo ""
echo -e "${YELLOW}Cleaning old builds...${NC}"
rm -rf dist/ build/ *.egg-info src/*.egg-info

# Build package
echo -e "${YELLOW}Building package...${NC}"
uv build || {
    echo -e "${RED}Build failed!${NC}"
    exit 1
}

echo ""
echo -e "${GREEN}Build successful!${NC}"
ls -lh dist/

# Ask which repository to publish to
echo ""
echo "Publish to:"
echo "  1) TestPyPI (recommended for testing)"
echo "  2) PyPI (production)"
echo "  3) Skip upload (just build)"
read -p "Choose (1/2/3): " choice

case $choice in
    1)
        echo -e "${YELLOW}Publishing to TestPyPI...${NC}"
        uv run twine upload --repository testpypi dist/*
        echo ""
        echo -e "${GREEN}Published to TestPyPI!${NC}"
        echo "Test installation with:"
        echo "  pip install --index-url https://test.pypi.org/simple/ anyt==$VERSION"
        ;;
    2)
        echo -e "${RED}WARNING: Publishing to production PyPI!${NC}"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo -e "${YELLOW}Publishing to PyPI...${NC}"
            uv run twine upload dist/*
            echo ""
            echo -e "${GREEN}Published to PyPI!${NC}"
            echo "Users can now install with:"
            echo "  pip install anyt==$VERSION"
            echo "  pipx install anyt==$VERSION"
            echo ""
            echo "Don't forget to:"
            echo "  - Create git tag: git tag v$VERSION"
            echo "  - Push tag: git push origin v$VERSION"
            echo "  - Create GitHub Release"
        else
            echo "Publishing cancelled."
        fi
        ;;
    3)
        echo -e "${GREEN}Build complete. Skipping upload.${NC}"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Done!${NC}"

