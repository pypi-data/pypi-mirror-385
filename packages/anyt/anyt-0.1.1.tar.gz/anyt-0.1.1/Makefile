.PHONY: install clean help lint format typecheck test test-all test-cli-unit test-cli-integration build publish install-local

help:
	@echo "Available commands:"
	@echo "  make install          - Install dependencies"
	@echo "  make clean            - Clean Python cache files"
	@echo "  make lint             - Run ruff check"
	@echo "  make format           - Run ruff format"
	@echo "  make typecheck        - Run mypy type checking"
	@echo "  make test             - Run unit tests only (default)"
	@echo "  make test-all         - Run both unit and integration tests"
	@echo "  make test-cli-unit    - Run CLI unit tests only"
	@echo "  make test-cli-integration - Run CLI integration tests (requires backend)"
	@echo "  make build            - Build distribution packages"
	@echo "  make publish          - Publish to PyPI"
	@echo "  make install-local    - Install package locally for development"

install:
	uv sync

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf dist/ build/ *.egg-info

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	@echo "Type checking src/..."
	@uv run mypy src
	@echo "Type checking tests/..."
	@uv run mypy tests

test:
	@echo "Running unit tests only..."
	@echo "(Use 'make test-all' to include integration tests)"
	PYTHONPATH=src uv run pytest tests/cli/unit/ -v

test-all:
	@echo "Running all tests (unit + integration)..."
	@echo "Note: Integration tests require a running backend server"
	PYTHONPATH=src uv run pytest tests/cli/ -v

test-cli-unit:
	@echo "Running CLI unit tests..."
	PYTHONPATH=src uv run pytest tests/cli/unit/ -v

test-cli-integration:
	@echo "Running CLI integration tests..."
	@echo "Note: Requires backend server running at http://localhost:8000"
	PYTHONPATH=src uv run pytest tests/cli/integration/ -v

build:
	@echo "Building distribution packages..."
	uv build

publish:
	@echo "Publishing to PyPI..."
	@./scripts/publish.sh

install-local:
	@echo "Installing package locally..."
	@./scripts/install_local.sh
