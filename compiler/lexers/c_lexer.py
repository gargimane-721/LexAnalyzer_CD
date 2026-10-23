"""
C Language Lexical Analyzer.
Recognizes full C keywords, operators, preprocessor directives, comments, strings,
and character literals while preserving all original educational C subset tokens and diagnostics.
"""

import re
from typing import List, Tuple
from compiler.tokens import Token, TokenType, C_KEYWORDS
from compiler.diagnostics import Diagnostic, DiagnosticPhase
from .base_lexer import BaseLexer


class CLexer(BaseLexer):
    """Lexer for C programming language with accurate spatial tracking."""

    # Ordered token specifications: multi-char patterns before single-char patterns
    TOKEN_SPECIFICATION = [
        ("PREPROCESSOR",   r"#[a-zA-Z_]+([^\n\\]|\\.)*"),       # #include <stdio.h>, #define
        ("COMMENT_BLOCK",  r"/\*[\s\S]*?\*/"),                   # Multi-line comment /* ... */
        ("COMMENT_LINE",   r"//[^\n]*"),                         # Single-line comment // ...
        ("MALFORMED_NUM",  r"\d+\.\d+(\.\d+)+"),                 # Multiple decimal points: e.g. 1.2.3
        ("BAD_IDENTIFIER", r"\d+[a-zA-Z_][a-zA-Z0-9_]*"),        # Number prefixing identifier: e.g. 12abc
        ("FLOAT_LITERAL",  r"\d+\.\d+([eE][+-]?\d+)?[fF]?"),     # Float literal: e.g. 3.14, 5.5f
        ("INT_LITERAL",    r"0[xX][0-9a-fA-F]+|\d+"),            # Hex or decimal integer: e.g. 0xFF, 42
        ("STRING_LITERAL", r'"(?:\\.|[^"\\])*"'),                # "Hello, world!"
        ("CHAR_LITERAL",   r"'(?:\\.|[^'\\])'"),                 # 'c', '\n'
        ("UNTERM_STRING",  r'"(?:\\.|[^"\\])*$'),                # Unterminated string
        ("UNTERM_CHAR",    r"'(?:\\.|[^'\\])*$"),                # Unterminated char
        ("OP_EQ",          r"=="),                               # Equal comparison
        ("OP_NE",          r"!="),                               # Not equal comparison
        ("OP_LE",          r"<="),                               # Less than or equal
        ("OP_GE",          r">="),                               # Greater than or equal
        ("OP_LOGICAL_AND", r"&&"),                               # Logical AND
        ("OP_LOGICAL_OR",  r"\|\|"),                             # Logical OR
        ("OP_INC",         r"\+\+"),                             # Increment ++
        ("OP_DEC",         r"--"),                               # Decrement --
        ("OP_PLUS_ASSIGN", r"\+="),                              # +=
        ("OP_MINUS_ASSIGN",r"-="),                               # -=
        ("OP_MUL_ASSIGN",  r"\*="),                              # *=
        ("OP_DIV_ASSIGN",  r"/="),                               # /=
        ("OP_ASSIGN",      r"="),                                # Assignment =
        ("OP_PLUS",        r"\+"),                               # Addition +
        ("OP_MINUS",       r"-"),                                # Subtraction -
        ("OP_MULTIPLY",    r"\*"),                               # Multiplication *
        ("OP_DIVIDE",      r"/"),                                # Division /
        ("OP_MOD",         r"%"),                                # Modulo %
        ("OP_LT",          r"<"),                                # Less than <
        ("OP_GT",          r">"),                                # Greater than >
        ("OP_LOGICAL_NOT", r"!"),                                # Logical NOT !
        ("OP_BIT_AND",     r"&"),                                # Bitwise AND &
        ("OP_BIT_OR",      r"\|"),                               # Bitwise OR |
        ("OP_BIT_XOR",     r"\^"),                               # Bitwise XOR ^
        ("OP_BIT_NOT",     r"~"),                                # Bitwise NOT ~
        ("SEMICOLON",      r";"),                                # Semicolon ;
        ("COMMA",          r","),                                # Comma ,
        ("DOT",            r"\."),                               # Dot .
        ("LPAREN",         r"\("),                               # (
        ("RPAREN",         r"\)"),                               # )
        ("LBRACE",         r"\{"),                               # {
        ("RBRACE",         r"\}"),                               # }
        ("LBRACKET",       r"\["),                               # [
        ("RBRACKET",       r"\]"),                               # ]
        ("IDENTIFIER",     r"[a-zA-Z_][a-zA-Z0-9_]*"),           # Identifiers & keywords
        ("WHITESPACE",     r"[ \t]+"),                           # Horizontal whitespace
        ("NEWLINE",        r"\r?\n"),                            # Line break
        ("UNKNOWN",        r"."),                                # Any illegal character
    ]

    MASTER_REGEX = re.compile(
        "|".join(f"(?P<{pair[0]}>{pair[1]})" for pair in TOKEN_SPECIFICATION)
    )

    def tokenize(self) -> Tuple[List[Token], List[Diagnostic]]:
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

            elif kind in ("COMMENT_LINE", "COMMENT_BLOCK"):
                newlines_in_comment = lexeme.count("\n")
                if newlines_in_comment > 0:
                    line_num += newlines_in_comment
                    line_start = match.end() - (len(lexeme) - lexeme.rfind("\n") - 1)
                continue

            elif kind == "PREPROCESSOR":
                self.tokens.append(Token(TokenType.PREPROCESSOR, lexeme, line_num, column))

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

            elif kind == "UNTERM_STRING":
                self.diagnostics.append(
                    Diagnostic(
                        phase=DiagnosticPhase.LEXICAL,
                        error_code="LEX004",
                        message="Unterminated string literal.",
                        line=line_num,
                        column=column,
                        suggestion="Close the string with a matching double quotation mark '\"'."
                    )
                )
                self.tokens.append(Token(TokenType.UNKNOWN, lexeme, line_num, column))

            elif kind == "UNTERM_CHAR":
                self.diagnostics.append(
                    Diagnostic(
                        phase=DiagnosticPhase.LEXICAL,
                        error_code="LEX004",
                        message="Unterminated character literal.",
                        line=line_num,
                        column=column,
                        suggestion="Close the character constant with a matching single quote '''."
                    )
                )
                self.tokens.append(Token(TokenType.UNKNOWN, lexeme, line_num, column))

            elif kind == "FLOAT_LITERAL":
                clean_val = lexeme.rstrip("fF")
                self.tokens.append(
                    Token(TokenType.FLOAT_LITERAL, lexeme, line_num, column, value=float(clean_val))
                )

            elif kind == "INT_LITERAL":
                base = 16 if lexeme.lower().startswith("0x") else 10
                self.tokens.append(
                    Token(TokenType.INT_LITERAL, lexeme, line_num, column, value=int(lexeme, base))
                )

            elif kind == "STRING_LITERAL":
                clean_str = lexeme[1:-1].encode().decode("unicode_escape", errors="ignore")
                self.tokens.append(
                    Token(TokenType.STRING_LITERAL, lexeme, line_num, column, value=clean_str)
                )

            elif kind == "CHAR_LITERAL":
                self.tokens.append(
                    Token(TokenType.CHAR_LITERAL, lexeme, line_num, column, value=lexeme[1:-1])
                )

            elif kind == "IDENTIFIER":
                if lexeme in C_KEYWORDS:
                    self.tokens.append(Token(C_KEYWORDS[lexeme], lexeme, line_num, column))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, lexeme, line_num, column))

            elif kind.startswith("OP_") or kind in (
                "SEMICOLON", "COMMA", "DOT", "LPAREN", "RPAREN", "LBRACE", "RBRACE", "LBRACKET", "RBRACKET"
            ):
                token_type = getattr(TokenType, kind, TokenType.UNKNOWN)
                self.tokens.append(Token(token_type, lexeme, line_num, column))

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

        final_col = len(self.source_code) - line_start + 1
        self.tokens.append(Token(TokenType.EOF, "<EOF>", line_num, final_col))
        return self.tokens, self.diagnostics

