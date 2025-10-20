"""Provide version information."""

__version__ = "7.3.0"

import sys

try:
    import ansible  # noqa
except ImportError:
    sys.exit("ERROR: Python requirements are missing: 'ansible-core' not found.")
