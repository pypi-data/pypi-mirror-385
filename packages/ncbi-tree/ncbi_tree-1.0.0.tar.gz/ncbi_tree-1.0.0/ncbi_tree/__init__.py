"""
VERSION: 2025-10-21
AUTHOR: NCBI-Tree Contributors
LICENSE: Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0)
"""

__version__ = "1.0.0"
__author__ = "NCBI-Tree Contributors"
__license__ = "CC BY-NC 4.0"

from .core import build_ncbi_tree, download_and_extract_taxonomy

__all__ = ["build_ncbi_tree", "download_and_extract_taxonomy", "__version__"]
