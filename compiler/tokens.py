"""
Token definitions and classifications for the C-like source language.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional


class TokenType(str, Enum):
    # Keywords
    KEYWORD_INT = "KEYWORD_INT"
    KEYWORD_FLOAT = "KEYWORD_FLOAT"
    KEYWORD_PRINT = "KEYWORD_PRINT"

    # Identifiers & Literals
    IDENTIFIER = "IDENTIFIER"
    INT_LITERAL = "INT_LITERAL"
    FLOAT_LITERAL = "FLOAT_LITERAL"

    # Operators
    OP_ASSIGN = "OP_ASSIGN"       # =
    OP_PLUS = "OP_PLUS"           # +
    OP_MINUS = "OP_MINUS"         # -
    OP_MULTIPLY = "OP_MULTIPLY"   # *
    OP_DIVIDE = "OP_DIVIDE"       # /

    # Separators / Delimiters
    SEMICOLON = "SEMICOLON"       # ;
    LPAREN = "LPAREN"             # (
    RPAREN = "RPAREN"             # )

    # Special / EOF
    EOF = "EOF"
    UNKNOWN = "UNKNOWN"

    def category(self) -> str:
        """Returns the high-level category of the token for statistical reporting."""
        if self.name.startswith("KEYWORD"):
            return "Keyword"
        if self in (TokenType.INT_LITERAL, TokenType.FLOAT_LITERAL):
            return "Literal"
        if self == TokenType.IDENTIFIER:
            return "Identifier"
        if self.name.startswith("OP_"):
            return "Operator"
        if self in (TokenType.SEMICOLON, TokenType.LPAREN, TokenType.RPAREN):
            return "Separator"
        return "Special"


KEYWORDS = {
    "int": TokenType.KEYWORD_INT,
    "float": TokenType.KEYWORD_FLOAT,
    "print": TokenType.KEYWORD_PRINT,
}


@dataclass
class Token:
    """Represents a lexical token recognized in the source code."""
    token_type: TokenType
    lexeme: str
    line: int
    column: int
    value: Optional[Any] = None

    def to_dict(self) -> dict:
        return {
            "token_type": self.token_type.value,
            "category": self.token_type.category(),
            "lexeme": self.lexeme,
            "line": self.line,
            "column": self.column,
            "value": self.value,
        }

    def __repr__(self) -> str:
        return f"Token({self.token_type.name}, '{self.lexeme}', Ln {self.line}, Col {self.column})"

