"""
Valve Parsers - A Python library for parsing Valve game engine files

This library provides parsers for:
- VPK (Valve Package) files - Valve's archive format
- PCF (Particle Cache File) files - Valve's particle system files

Author: Extracted from casual-pre-loader project
License: MIT
"""

from .vpk import VPKFile, VPKDirectoryEntry
from .pcf import PCFFile, PCFElement
from .constants import PCFVersion, AttributeType

__version__ = "1.0.3"
__all__ = [
    "VPKFile", 
    "VPKDirectoryEntry",
    "PCFFile", 
    "PCFElement",
    "PCFVersion",
    "AttributeType"
]