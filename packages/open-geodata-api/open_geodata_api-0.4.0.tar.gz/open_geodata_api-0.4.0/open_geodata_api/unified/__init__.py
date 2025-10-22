"""
Unified STAC Client for Open Geodata API
========================================

A generic client for connecting to any STAC API endpoint.
Supports custom STAC APIs like DLR EOC, OpenEO, and others.
"""

from .client import UnifiedSTACClient

__version__ = "0.1.0"
__all__ = ["UnifiedSTACClient"]
