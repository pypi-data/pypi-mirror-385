"""Setup.py shim for backward compatibility with older build tools.

Modern Python packaging uses pyproject.toml instead of setup.py.
This file exists only for compatibility with legacy build systems.
"""

from setuptools import setup

# All configuration is in pyproject.toml
# This setup.py exists only for backward compatibility
setup()
