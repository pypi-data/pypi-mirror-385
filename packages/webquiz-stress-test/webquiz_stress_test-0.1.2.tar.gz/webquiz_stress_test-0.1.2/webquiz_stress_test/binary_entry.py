#!/usr/bin/env python3
"""
Entry point for PyInstaller binary.
"""

import sys
from webquiz_stress_test.cli import main


if __name__ == "__main__":
    sys.exit(main())
