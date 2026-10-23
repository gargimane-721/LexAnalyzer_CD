"""
Base Lexer Interface.
Defines the common scanning contract across all supported languages.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple
from compiler.tokens import Token
from compiler.diagnostics import Diagnostic


class BaseLexer(ABC):
    """Abstract base class for language-specific lexical analyzers."""

    def __init__(self, source_code: str):
        self.source_code = source_code
        self.tokens: List[Token] = []
        self.diagnostics: List[Diagnostic] = []

    @abstractmethod
    def tokenize(self) -> Tuple[List[Token], List[Diagnostic]]:
        """Scans the source code and returns a tuple of (tokens, diagnostics)."""
        pass

