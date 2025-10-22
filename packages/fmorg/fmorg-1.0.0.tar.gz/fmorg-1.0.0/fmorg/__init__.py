"""
FMORG - File Manager Organization Tool

A smart file organization tool that automatically sorts files into folders
based on intelligent filename analysis.
"""

__version__ = "1.0.0"
__author__ = "FMORG Team"

from .analyzer import FilenameAnalyzer
from .organizer import FileOrganizer
from .display import DisplayManager

__all__ = ["FilenameAnalyzer", "FileOrganizer", "DisplayManager"]