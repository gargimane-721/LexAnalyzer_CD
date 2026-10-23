"""
Lexical Analyzer (Scanner / Tokenizer) for the C-like source language.
Handles token classification, line/column tracking, whitespace/comment filtering,
and error reporting for illegal characters or malformed tokens.
"""

import re
from typing import List, Tuple
from .tokens import Token, TokenType, KEYWORDS
from .diagnostics import Diagnostic, DiagnosticPhase


class Lexer:
    """Hand-crafted regex-based scanner for C-like language."""

    # Pre-compiled regex patterns for precision tokenizing
    TOKEN_SPECIFICATION = [
        ("COMMENT",        r"//[^\n]*"),                     # Single-line comment
        ("MALFORMED_NUM",  r"\d+\.\d+(\.\d+)+"),             # Multiple decimal points: e.g. 1.2.3
        ("BAD_IDENTIFIER", r"\d+[a-zA-Z_][a-zA-Z0-9_]*"),    # Number prefixing identifier: e.g. 12abc
        ("FLOAT_LITERAL",  r"\d+\.\d+"),                     # Floating point literal: e.g. 3.14
        ("INT_LITERAL",    r"\d+"),                          # Integer literal: e.g. 42
        ("IDENTIFIER",     r"[a-zA-Z_][a-zA-Z0-9_]*"),       # Identifiers & keywords
        ("OP_ASSIGN",      r"="),                            # Assignment operator
        ("OP_PLUS",        r"\+"),                           # Addition operator
        ("OP_MINUS",       r"-"),                            # Subtraction operator
        ("OP_MULTIPLY",    r"\*"),                           # Multiplication operator
        ("OP_DIVIDE",      r"/"),                            # Division operator
        ("SEMICOLON",      r";"),                            # Statement terminator
        ("LPAREN",         r"\("),                           # Left parenthesis
        ("RPAREN",         r"\)"),                           # Right parenthesis
        ("WHITESPACE",     r"[ \t]+"),                       # Horizontal whitespace
        ("NEWLINE",        r"\r?\n"),                        # Line breaks
        ("UNKNOWN",        r"."),                            # Any other unrecognized character
    ]

    MASTER_REGEX = re.compile(
        "|".join(f"(?P<{pair[0]}>{pair[1]})" for pair in TOKEN_SPECIFICATION)
    )

    def __init__(self, source_code: str):
        self.source_code = source_code
        self.tokens: List[Token] = []
        self.diagnostics: List[Diagnostic] = []

    def tokenize(self) -> Tuple[List[Token], List[Diagnostic]]:
        """Scans the source code and produces a token stream with line & column tracking."""
        self.tokens = []
        self.diagnostics = []

        line_num = 1
        line_start = 0

        for match in self.MASTER_REGEX.finditer(self.source_code):
            kind = match.lastgroup
            lexeme = match.group()
            start_pos = match.start()
            column = start_pos - line_start + 1

            if kind == "WHITESPACE":
                continue

            elif kind == "NEWLINE":
                line_num += 1
                line_start = match.end()
                continue

            elif kind == "COMMENT":
                # Comments are ignored during syntax analysis, but line position is maintained
                continue

            elif kind == "MALFORMED_NUM":
                self.diagnostics.append(
                    Diagnostic(
                        phase=DiagnosticPhase.LEXICAL,
                        error_code="LEX002",
                        message=f"Malformed floating-point literal '{lexeme}' with multiple decimal points.",
                        line=line_num,
                        column=column,
                        suggestion="Ensure numeric constants have at most one decimal point (e.g. 5.5)."
                    )
                )
                self.tokens.append(Token(TokenType.UNKNOWN, lexeme, line_num, column))

            elif kind == "BAD_IDENTIFIER":
                self.diagnostics.append(
                    Diagnostic(
                        phase=DiagnosticPhase.LEXICAL,
                        error_code="LEX003",
                        message=f"Invalid identifier '{lexeme}': identifiers cannot begin with a digit.",
                        line=line_num,
                        column=column,
                        suggestion="Rename identifier to start with an alphabetic letter or underscore."
                    )
                )
                self.tokens.append(Token(TokenType.UNKNOWN, lexeme, line_num, column))

            elif kind == "FLOAT_LITERAL":
                self.tokens.append(
                    Token(
                        TokenType.FLOAT_LITERAL,
                        lexeme,
                        line_num,
                        column,
                        value=float(lexeme)
                    )
                )

            elif kind == "INT_LITERAL":
                self.tokens.append(
                    Token(
                        TokenType.INT_LITERAL,
                        lexeme,
                        line_num,
                        column,
                        value=int(lexeme)
                    )
                )

            elif kind == "IDENTIFIER":
                if lexeme in KEYWORDS:
                    self.tokens.append(
                        Token(KEYWORDS[lexeme], lexeme, line_num, column)
                    )
                else:
                    self.tokens.append(
                        Token(TokenType.IDENTIFIER, lexeme, line_num, column)
                    )

            elif kind == "OP_ASSIGN":
                self.tokens.append(Token(TokenType.OP_ASSIGN, lexeme, line_num, column))

            elif kind == "OP_PLUS":
                self.tokens.append(Token(TokenType.OP_PLUS, lexeme, line_num, column))

            elif kind == "OP_MINUS":
                self.tokens.append(Token(TokenType.OP_MINUS, lexeme, line_num, column))

            elif kind == "OP_MULTIPLY":
                self.tokens.append(Token(TokenType.OP_MULTIPLY, lexeme, line_num, column))

            elif kind == "OP_DIVIDE":
                self.tokens.append(Token(TokenType.OP_DIVIDE, lexeme, line_num, column))

            elif kind == "SEMICOLON":
                self.tokens.append(Token(TokenType.SEMICOLON, lexeme, line_num, column))

            elif kind == "LPAREN":
                self.tokens.append(Token(TokenType.LPAREN, lexeme, line_num, column))

            elif kind == "RPAREN":
                self.tokens.append(Token(TokenType.RPAREN, lexeme, line_num, column))

            elif kind == "UNKNOWN":
                self.diagnostics.append(
                    Diagnostic(
                        phase=DiagnosticPhase.LEXICAL,
                        error_code="LEX001",
                        message=f"Unrecognized or illegal character '{lexeme}'.",
                        line=line_num,
                        column=column,
                        suggestion=f"Remove or replace '{lexeme}' with supported C syntax characters."
                    )
                )
                self.tokens.append(Token(TokenType.UNKNOWN, lexeme, line_num, column))

        # Append EOF token
        final_col = len(self.source_code) - line_start + 1
        self.tokens.append(Token(TokenType.EOF, "<EOF>", line_num, final_col))

        return self.tokens, self.diagnostics

