"""Tests package initialization.

This module sets up the Python path to ensure tests can import backend modules.
"""

import sys
from pathlib import Path

# Add src directory to Python path
# This __init__.py is in tests/, so parent is project root
project_root = Path(__file__).parent.parent
src_path = str((project_root / "src").resolve())

if src_path not in sys.path:
    sys.path.insert(0, src_path)
