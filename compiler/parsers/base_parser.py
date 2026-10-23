"""
Base Parser Interface for multi-language syntax checking.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Any
from compiler.tokens import Token
from compiler.diagnostics import Diagnostic


class BaseParser(ABC):
    """Abstract base class for language-specific syntax checkers."""

    def __init__(self, tokens: List[Token], source_code: str = ""):
        self.tokens = tokens
        self.source_code = source_code
        self.diagnostics: List[Diagnostic] = []

    @abstractmethod
    def parse(self) -> Tuple[Optional[Any], List[Diagnostic]]:
        """Parses the token stream and returns (AST, diagnostics)."""
        pass

