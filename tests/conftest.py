"""Pytest fixtures shared across the new test suite."""

from __future__ import annotations

import sys
from pathlib import Path

# The mltb package expects to be imported with the project root on
# sys.path; make sure that's true regardless of where pytest is run.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
