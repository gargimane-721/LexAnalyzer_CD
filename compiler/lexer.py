"""
Backward-compatible wrapper for the C Lexical Analyzer.
Imports CLexer as Lexer to preserve existing test interfaces.
"""

from compiler.lexers.c_lexer import CLexer as Lexer

__all__ = ["Lexer"]
