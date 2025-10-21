"""
Purple Bindings - Fast C++ metadata scanner

High-performance C++ extension for scanning metadata files.
Provides 9x speedup over Python implementation.
"""

# Import the C++ extension
from metadata_scanner import *

__version__ = "0.8.0"
__all__ = ['scan_metadata']

