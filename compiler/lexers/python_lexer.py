"""
Python Language Lexical Analyzer.
Recognizes Python keywords, identifiers, numeric literals, triple/single-quoted strings,
operators, delimiters, comments (#), and significant indentation (INDENT, DEDENT, NEWLINE).
"""

import re
from typing import List, Tuple
from compiler.tokens import Token, TokenType, PYTHON_KEYWORDS
from compiler.diagnostics import Diagnostic, DiagnosticPhase
from .base_lexer import BaseLexer


class PythonLexer(BaseLexer):
    """Lexical analyzer for Python with indentation and dedentation tracking."""

    TOKEN_SPECIFICATION = [
        ("COMMENT",         r"#[^\n]*"),                                # # comment
        ("TRIPLE_STRING_D", r'"""[\s\S]*?"""'),                         # """ docstring """
        ("TRIPLE_STRING_S", r"'''[\s\S]*?'''"),                         # ''' docstring '''
        ("UNTERM_TRIPLE_D", r'"""[\s\S]*$'),                            # Unterminated """
        ("UNTERM_TRIPLE_S", r"'''[\s\S]*$"),                            # Unterminated '''
        ("STRING_D",        r'"(\\.|[^\\"\n])*"'),                      # "string"
        ("STRING_S",        r"'(\\.|[^\\'\n])*'"),                      # 'string'
        ("UNTERM_STRING",   r'["\'](\\.|[^\\"\n])*$'),                  # Unterminated single line string
        ("FLOAT_LITERAL",   r"\d+\.\d+([eE][+-]?\d+)?j?|\d+[eE][+-]?\d+j?"), # 3.14, 1e-4, 2.5j
        ("INT_LITERAL",     r"0[xX][0-9a-fA-F]+|0[bB][01]+|0[oO][0-7]+|\d+j?"), # Hex, bin, oct, dec, complex int
        ("OP_POWER",        r"\*\*"),                                   # **
        ("OP_FLOORDIV",     r"//"),                                     # //
        ("OP_EQ",           r"=="),                                     # ==
        ("OP_NE",           r"!="),                                     # !=
        ("OP_LE",           r"<="),                                     # <=
        ("OP_GE",           r">="),                                     # >=
        ("OP_PLUS_ASSIGN",  r"\+="),                                    # +=
        ("OP_MINUS_ASSIGN", r"-="),                                     # -=
        ("OP_MUL_ASSIGN",   r"\*="),                                    # *=
        ("OP_DIV_ASSIGN",   r"/="),                                     # /=
        ("OP_ASSIGN",       r"="),                                      # =
        ("OP_PLUS",         r"\+"),                                     # +
        ("OP_MINUS",        r"-"),                                      # -
        ("OP_MULTIPLY",     r"\*"),                                     # *
        ("OP_DIVIDE",       r"/"),                                      # /
        ("OP_MOD",          r"%"),                                      # %
        ("OP_LT",           r"<"),                                      # <
        ("OP_GT",           r">"),                                      # >
        ("OP_BIT_AND",      r"&"),                                      # &
        ("OP_BIT_OR",       r"\|"),                                     # |
        ("OP_BIT_XOR",      r"\^"),                                     # ^
        ("OP_BIT_NOT",      r"~"),                                      # ~
        ("COLON",           r":"),                                      # :
        ("COMMA",           r","),                                      # ,
        ("DOT",             r"\."),                                     # .
        ("SEMICOLON",       r";"),                                      # ; (optional in python)
        ("LPAREN",          r"\("),                                     # (
        ("RPAREN",          r"\)"),                                     # )
        ("LBRACE",          r"\{"),                                     # {
        ("RBRACE",          r"\}"),                                     # }
        ("LBRACKET",        r"\["),                                     # [
        ("RBRACKET",        r"\]"),                                     # ]
        ("IDENTIFIER",      r"[a-zA-Z_][a-zA-Z0-9_]*"),                 # Identifiers & keywords
        ("WHITESPACE",      r"[ \t]+"),                                 # Spaces / tabs
        ("NEWLINE",         r"\r?\n"),                                  # Line break
        ("UNKNOWN",         r"."),                                      # Unknown character
    ]

    MASTER_REGEX = re.compile(
        "|".join(f"(?P<{pair[0]}>{pair[1]})" for pair in TOKEN_SPECIFICATION)
    )

    def tokenize(self) -> Tuple[List[Token], List[Diagnostic]]:
        self.tokens = []
        self.diagnostics = []

        indent_stack = [0]
        lines = self.source_code.splitlines(keepends=True)
        line_num = 1

        for line in lines:
            line_str = line.rstrip("\r\n")
            stripped = line_str.lstrip(" \t")

            # Check if this line is purely whitespace or a comment
            if not stripped or stripped.startswith("#"):
                # Handle any inline comment if present
                if stripped.startswith("#"):
                    # Comments do not change indentation
                    pass
                line_num += 1
                continue

            # Calculate indentation level (tab = 4 spaces)
            raw_leading = line_str[:len(line_str) - len(stripped)]
            indent_level = 0
            for ch in raw_leading:
                if ch == " ":
                    indent_level += 1
                elif ch == "\t":
                    indent_level = (indent_level // 4 + 1) * 4

            current_indent = indent_stack[-1]

            if indent_level > current_indent:
                indent_stack.append(indent_level)
                self.tokens.append(Token(TokenType.INDENT, "<INDENT>", line_num, 1))

            elif indent_level < current_indent:
                while indent_stack and indent_stack[-1] > indent_level:
                    indent_stack.pop()
                    self.tokens.append(Token(TokenType.DEDENT, "<DEDENT>", line_num, 1))

                if not indent_stack or indent_stack[-1] != indent_level:
                    self.diagnostics.append(
                        Diagnostic(
                            phase=DiagnosticPhase.LEXICAL,
                            error_code="LEX005",
                            message=f"IndentationError: unindent does not match any outer indentation level at line {line_num}.",
                            line=line_num,
                            column=1,
                            suggestion="Ensure consistent indentation using 4 spaces per block level."
                        )
                    )

            # Tokenize the line content
            line_offset = len(raw_leading)
            col_base = line_offset + 1

            for match in self.MASTER_REGEX.finditer(stripped):
                kind = match.lastgroup
                lexeme = match.group()
                column = col_base + match.start()

                if kind == "WHITESPACE":
                    continue

                elif kind == "NEWLINE":
                    continue

                elif kind == "COMMENT":
                    continue

                elif kind in ("UNTERM_TRIPLE_D", "UNTERM_TRIPLE_S", "UNTERM_STRING"):
                    self.diagnostics.append(
                        Diagnostic(
                            phase=DiagnosticPhase.LEXICAL,
                            error_code="LEX004",
                            message=f"SyntaxError: EOL while scanning string literal at line {line_num}.",
                            line=line_num,
                            column=column,
                            suggestion="Close string with matching quotation marks."
                        )
                    )
                    self.tokens.append(Token(TokenType.UNKNOWN, lexeme, line_num, column))

                elif kind in ("TRIPLE_STRING_D", "TRIPLE_STRING_S", "STRING_D", "STRING_S"):
                    delim = lexeme[:3] if lexeme.startswith(('"""', "'''")) else lexeme[0]
                    content = lexeme[len(delim):-len(delim)]
                    self.tokens.append(
                        Token(TokenType.STRING_LITERAL, lexeme, line_num, column, value=content)
                    )

                elif kind == "FLOAT_LITERAL":
                    val = float(lexeme.rstrip("jJ")) if not lexeme.endswith(("j", "J")) else complex(lexeme)
                    self.tokens.append(Token(TokenType.FLOAT_LITERAL, lexeme, line_num, column, value=val))

                elif kind == "INT_LITERAL":
                    val = int(lexeme, 0) if not lexeme.endswith(("j", "J")) else complex(lexeme)
                    self.tokens.append(Token(TokenType.INT_LITERAL, lexeme, line_num, column, value=val))

                elif kind == "IDENTIFIER":
                    if lexeme in PYTHON_KEYWORDS:
                        self.tokens.append(Token(PYTHON_KEYWORDS[lexeme], lexeme, line_num, column))
                    else:
                        self.tokens.append(Token(TokenType.IDENTIFIER, lexeme, line_num, column))

                elif kind.startswith("OP_") or kind in (
                    "COLON", "COMMA", "DOT", "SEMICOLON", "LPAREN", "RPAREN", "LBRACE", "RBRACE", "LBRACKET", "RBRACKET"
                ):
                    token_type = getattr(TokenType, kind, TokenType.UNKNOWN)
                    self.tokens.append(Token(token_type, lexeme, line_num, column))

                elif kind == "UNKNOWN":
                    self.diagnostics.append(
                        Diagnostic(
                            phase=DiagnosticPhase.LEXICAL,
                            error_code="LEX001",
                            message=f"Unrecognized character '{lexeme}' in Python source.",
                            line=line_num,
                            column=column,
                            suggestion=f"Remove or replace '{lexeme}' with valid Python syntax."
                        )
                    )
                    self.tokens.append(Token(TokenType.UNKNOWN, lexeme, line_num, column))

            # End of statement line emits a NEWLINE token
            self.tokens.append(Token(TokenType.NEWLINE, "<NEWLINE>", line_num, len(line_str) + 1))
            line_num += 1

        # Pop any remaining indentation levels to 0 at EOF
        while len(indent_stack) > 1:
            indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, "<DEDENT>", line_num, 1))

        self.tokens.append(Token(TokenType.EOF, "<EOF>", line_num, 1))
        return self.tokens, self.diagnostics

