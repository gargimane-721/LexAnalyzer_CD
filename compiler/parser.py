"""
Backward-compatible wrapper for the C Syntax Checker (Parser).
Imports CParser as Parser to preserve existing test interfaces.
"""

from compiler.parsers.c_parser import CParser as Parser

__all__ = ["Parser"]
