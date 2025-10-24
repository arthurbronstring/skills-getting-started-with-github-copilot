"""
Shared test configuration for pytest
"""
import pytest
import sys
from pathlib import Path

# Add the src directory to the Python path so we can import the app
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))