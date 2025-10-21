"""Pytest configuration and fixtures for CLI testing."""

import sys
from pathlib import Path

# Add src and tests directories to Python path
project_root = Path(__file__).parent.parent
src_path = str((project_root / "src").resolve())
tests_path = str((project_root / "tests").resolve())

# Insert at position 0 to ensure priority
sys.path.insert(0, tests_path)
sys.path.insert(0, src_path)


def pytest_configure(config):
    """Pytest hook that runs before test collection.

    Ensures Python path is set up correctly for all test modules.
    """
    # Ensure paths are set up
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    if tests_path not in sys.path:
        sys.path.insert(0, tests_path)
