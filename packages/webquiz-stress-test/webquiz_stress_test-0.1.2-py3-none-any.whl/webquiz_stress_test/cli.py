#!/usr/bin/env python3
"""CLI entry point for webquiz-stress-test"""

import sys
from .stress_test import main as stress_test_main


def main():
    """Main CLI entry point"""
    try:
        sys.exit(stress_test_main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)


if __name__ == "__main__":
    main()
