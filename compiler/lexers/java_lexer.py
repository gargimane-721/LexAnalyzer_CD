"""
Java Language Lexical Analyzer.
Recognizes Java keywords, identifiers, annotations (@Override), character and string literals,
numeric constants, comments (//, /* */, /** */), and operators.
"""

import re
from typing import List, Tuple
from compiler.tokens import Token, TokenType, JAVA_KEYWORDS
from compiler.diagnostics import Diagnostic, DiagnosticPhase
from .base_lexer import BaseLexer


class JavaLexer(BaseLexer):
    """Lexical analyzer for the Java programming language."""

    TOKEN_SPECIFICATION = [
        ("COMMENT_DOC",    r"/\*\*[\s\S]*?\*/"),                        # /** javadoc */
        ("COMMENT_BLOCK",  r"/\*[\s\S]*?\*/"),                          # /* comment */
        ("COMMENT_LINE",   r"//[^\n]*"),                                # // comment
        ("ANNOTATION",     r"@[a-zA-Z_][a-zA-Z0-9_]*"),                 # @Override, @Deprecated
        ("MALFORMED_NUM",  r"\d+\.\d+(\.\d+)+"),                        # 1.2.3
        ("BAD_IDENTIFIER", r"\d+[a-zA-Z_$][a-zA-Z0-9_$]*"),             # 123var
        ("FLOAT_LITERAL",  r"\d+\.\d+([eE][+-]?\d+)?[fFdD]?|\d+[fFdD]"), # 3.14f, 2.0d
        ("INT_LITERAL",    r"0[xX][0-9a-fA-F]+[lL]?|0[bB][01]+[lL]?|\d+[lL]?"), # 42, 100L, 0xFF
        ("STRING_LITERAL", r'"(?:\\.|[^"\\])*"'),                       # "text"
        ("CHAR_LITERAL",   r"'(?:\\.|[^'\\])'"),                        # 'c'
        ("UNTERM_STRING",  r'"(?:\\.|[^"\\])*$'),                       # Unterminated string
        ("UNTERM_CHAR",    r"'(?:\\.|[^'\\])*$"),                       # Unterminated char
        ("OP_EQ",          r"=="),                                      # ==
        ("OP_NE",          r"!="),                                      # !=
        ("OP_LE",          r"<="),                                      # <=
        ("OP_GE",          r">="),                                      # >=
        ("OP_LOGICAL_AND", r"&&"),                                      # &&
        ("OP_LOGICAL_OR",  r"\|\|"),                                    # ||
        ("OP_INC",         r"\+\+"),                                    # ++
        ("OP_DEC",         r"--"),                                      # --
        ("OP_PLUS_ASSIGN", r"\+="),                                     # +=
        ("OP_MINUS_ASSIGN",r"-="),                                      # -=
        ("OP_MUL_ASSIGN",  r"\*="),                                     # *=
        ("OP_DIV_ASSIGN",  r"/="),                                      # /=
        ("OP_ASSIGN",      r"="),                                       # =
        ("OP_PLUS",        r"\+"),                                      # +
        ("OP_MINUS",       r"-"),                                       # -
        ("OP_MULTIPLY",    r"\*"),                                      # *
        ("OP_DIVIDE",      r"/"),                                       # /
        ("OP_MOD",         r"%"),                                       # %
        ("OP_LT",          r"<"),                                       # <
        ("OP_GT",          r">"),                                       # >
        ("OP_LOGICAL_NOT", r"!"),                                       # !
        ("OP_BIT_AND",     r"&"),                                       # &
        ("OP_BIT_OR",      r"\|"),                                      # |
        ("OP_BIT_XOR",     r"\^"),                                      # ^
        ("OP_BIT_NOT",     r"~"),                                       # ~
        ("SEMICOLON",      r";"),                                       # ;
        ("COMMA",          r","),                                       # ,
        ("DOT",            r"\."),                                      # .
        ("LPAREN",         r"\("),                                      # (
        ("RPAREN",         r"\)"),                                      # )
        ("LBRACE",         r"\{"),                                      # {
        ("RBRACE",         r"\}"),                                      # }
        ("LBRACKET",       r"\["),                                      # [
        ("RBRACKET",       r"\]"),                                      # ]
        ("IDENTIFIER",     r"[a-zA-Z_$][a-zA-Z0-9_$]*"),                # Java identifiers
        ("WHITESPACE",     r"[ \t]+"),                                  # Spaces / tabs
        ("NEWLINE",        r"\r?\n"),                                   # Line break
        ("UNKNOWN",        r"."),                                       # Illegal char
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

            elif kind in ("COMMENT_LINE", "COMMENT_BLOCK", "COMMENT_DOC"):
                newlines = lexeme.count("\n")
                if newlines > 0:
                    line_num += newlines
                    line_start = match.end() - (len(lexeme) - lexeme.rfind("\n") - 1)
                continue

            elif kind == "ANNOTATION":
                self.tokens.append(Token(TokenType.ANNOTATION, lexeme, line_num, column))

            elif kind == "MALFORMED_NUM":
                self.diagnostics.append(
                    Diagnostic(
                        phase=DiagnosticPhase.LEXICAL,
                        error_code="LEX002",
                        message=f"Malformed numeric literal '{lexeme}' in Java source.",
                        line=line_num,
                        column=column,
                        suggestion="Ensure floating-point literals have at most one decimal point."
                    )
                )
                self.tokens.append(Token(TokenType.UNKNOWN, lexeme, line_num, column))

            elif kind == "BAD_IDENTIFIER":
                self.diagnostics.append(
                    Diagnostic(
                        phase=DiagnosticPhase.LEXICAL,
                        error_code="LEX003",
                        message=f"Invalid Java identifier '{lexeme}': cannot begin with a digit.",
                        line=line_num,
                        column=column,
                        suggestion="Rename identifier to start with an alphabetic letter, '$', or '_'."
                    )
                )
                self.tokens.append(Token(TokenType.UNKNOWN, lexeme, line_num, column))

            elif kind == "UNTERM_STRING":
                self.diagnostics.append(
                    Diagnostic(
                        phase=DiagnosticPhase.LEXICAL,
                        error_code="LEX004",
                        message="Unterminated string literal in Java source.",
                        line=line_num,
                        column=column,
                        suggestion="Close string literal with a matching double quotation mark '\"'."
                    )
                )
                self.tokens.append(Token(TokenType.UNKNOWN, lexeme, line_num, column))

            elif kind == "UNTERM_CHAR":
                self.diagnostics.append(
                    Diagnostic(
                        phase=DiagnosticPhase.LEXICAL,
                        error_code="LEX004",
                        message="Unterminated character literal in Java source.",
                        line=line_num,
                        column=column,
                        suggestion="Close character literal with a matching single quote '''."
                    )
                )
                self.tokens.append(Token(TokenType.UNKNOWN, lexeme, line_num, column))

            elif kind == "FLOAT_LITERAL":
                clean_val = lexeme.rstrip("fFdD")
                self.tokens.append(Token(TokenType.FLOAT_LITERAL, lexeme, line_num, column, value=float(clean_val)))

            elif kind == "INT_LITERAL":
                clean_val = lexeme.rstrip("lL")
                base = 16 if clean_val.lower().startswith("0x") else (2 if clean_val.lower().startswith("0b") else 10)
                self.tokens.append(Token(TokenType.INT_LITERAL, lexeme, line_num, column, value=int(clean_val, base)))

            elif kind == "STRING_LITERAL":
                clean_str = lexeme[1:-1].encode().decode("unicode_escape", errors="ignore")
                self.tokens.append(Token(TokenType.STRING_LITERAL, lexeme, line_num, column, value=clean_str))

            elif kind == "CHAR_LITERAL":
                self.tokens.append(Token(TokenType.CHAR_LITERAL, lexeme, line_num, column, value=lexeme[1:-1]))

            elif kind == "IDENTIFIER":
                if lexeme in JAVA_KEYWORDS:
                    self.tokens.append(Token(JAVA_KEYWORDS[lexeme], lexeme, line_num, column))
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
                        message=f"Unrecognized character '{lexeme}' in Java source.",
                        line=line_num,
                        column=column,
                        suggestion=f"Remove or replace '{lexeme}' with valid Java syntax."
                    )
                )
                self.tokens.append(Token(TokenType.UNKNOWN, lexeme, line_num, column))

        final_col = len(self.source_code) - line_start + 1
        self.tokens.append(Token(TokenType.EOF, "<EOF>", line_num, final_col))
        return self.tokens, self.diagnostics

