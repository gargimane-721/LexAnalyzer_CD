"""
Token definitions and classifications for C, Python, and Java.
Maintains 100% backward compatibility with the original C-like educational grammar.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional, Dict, Set


class TokenType(str, Enum):
    # Core & Existing Keywords (Preserved for compatibility)
    KEYWORD_INT = "KEYWORD_INT"
    KEYWORD_FLOAT = "KEYWORD_FLOAT"
    KEYWORD_PRINT = "KEYWORD_PRINT"

    # Extended C & Java Type Keywords
    KEYWORD_CHAR = "KEYWORD_CHAR"
    KEYWORD_DOUBLE = "KEYWORD_DOUBLE"
    KEYWORD_VOID = "KEYWORD_VOID"
    KEYWORD_BOOLEAN = "KEYWORD_BOOLEAN"
    KEYWORD_STRING = "KEYWORD_STRING"

    # Control Flow Keywords
    KEYWORD_IF = "KEYWORD_IF"
    KEYWORD_ELIF = "KEYWORD_ELIF"
    KEYWORD_ELSE = "KEYWORD_ELSE"
    KEYWORD_FOR = "KEYWORD_FOR"
    KEYWORD_WHILE = "KEYWORD_WHILE"
    KEYWORD_RETURN = "KEYWORD_RETURN"
    KEYWORD_SWITCH = "KEYWORD_SWITCH"
    KEYWORD_CASE = "KEYWORD_CASE"
    KEYWORD_BREAK = "KEYWORD_BREAK"
    KEYWORD_CONTINUE = "KEYWORD_CONTINUE"

    # Function, Class & OOP Keywords
    KEYWORD_DEF = "KEYWORD_DEF"
    KEYWORD_CLASS = "KEYWORD_CLASS"
    KEYWORD_STRUCT = "KEYWORD_STRUCT"
    KEYWORD_PUBLIC = "KEYWORD_PUBLIC"
    KEYWORD_PRIVATE = "KEYWORD_PRIVATE"
    KEYWORD_PROTECTED = "KEYWORD_PROTECTED"
    KEYWORD_STATIC = "KEYWORD_STATIC"
    KEYWORD_NEW = "KEYWORD_NEW"
    KEYWORD_THIS = "KEYWORD_THIS"
    KEYWORD_EXTENDS = "KEYWORD_EXTENDS"
    KEYWORD_IMPLEMENTS = "KEYWORD_IMPLEMENTS"

    # Import & Module Keywords
    KEYWORD_IMPORT = "KEYWORD_IMPORT"
    KEYWORD_FROM = "KEYWORD_FROM"
    KEYWORD_PACKAGE = "KEYWORD_PACKAGE"

    # Exception & Context Keywords
    KEYWORD_TRY = "KEYWORD_TRY"
    KEYWORD_EXCEPT = "KEYWORD_EXCEPT"
    KEYWORD_CATCH = "KEYWORD_CATCH"
    KEYWORD_FINALLY = "KEYWORD_FINALLY"
    KEYWORD_WITH = "KEYWORD_WITH"
    KEYWORD_AS = "KEYWORD_AS"
    KEYWORD_PASS = "KEYWORD_PASS"

    # Python Logical / Membership Keywords
    KEYWORD_AND = "KEYWORD_AND"
    KEYWORD_OR = "KEYWORD_OR"
    KEYWORD_NOT = "KEYWORD_NOT"
    KEYWORD_IN = "KEYWORD_IN"
    KEYWORD_IS = "KEYWORD_IS"

    # Special Value Keywords
    KEYWORD_TRUE = "KEYWORD_TRUE"
    KEYWORD_FALSE = "KEYWORD_FALSE"
    KEYWORD_NONE = "KEYWORD_NONE"
    KEYWORD_NULL = "KEYWORD_NULL"

    # Identifiers & Literals
    IDENTIFIER = "IDENTIFIER"
    INT_LITERAL = "INT_LITERAL"
    FLOAT_LITERAL = "FLOAT_LITERAL"
    STRING_LITERAL = "STRING_LITERAL"
    CHAR_LITERAL = "CHAR_LITERAL"

    # Operators (Arithmetic & Assignment)
    OP_ASSIGN = "OP_ASSIGN"             # =
    OP_PLUS = "OP_PLUS"                 # +
    OP_MINUS = "OP_MINUS"               # -
    OP_MULTIPLY = "OP_MULTIPLY"         # *
    OP_DIVIDE = "OP_DIVIDE"             # /
    OP_MOD = "OP_MOD"                   # %
    OP_POWER = "OP_POWER"               # **
    OP_FLOORDIV = "OP_FLOORDIV"         # //
    OP_PLUS_ASSIGN = "OP_PLUS_ASSIGN"   # +=
    OP_MINUS_ASSIGN = "OP_MINUS_ASSIGN" # -=
    OP_MUL_ASSIGN = "OP_MUL_ASSIGN"     # *=
    OP_DIV_ASSIGN = "OP_DIV_ASSIGN"     # /=

    # Relational & Logical Operators
    OP_EQ = "OP_EQ"                     # ==
    OP_NE = "OP_NE"                     # !=
    OP_LT = "OP_LT"                     # <
    OP_LE = "OP_LE"                     # <=
    OP_GT = "OP_GT"                     # >
    OP_GE = "OP_GE"                     # >=
    OP_LOGICAL_AND = "OP_LOGICAL_AND"   # &&
    OP_LOGICAL_OR = "OP_LOGICAL_OR"     # ||
    OP_LOGICAL_NOT = "OP_LOGICAL_NOT"   # !
    OP_INC = "OP_INC"                   # ++
    OP_DEC = "OP_DEC"                   # --

    # Bitwise Operators
    OP_BIT_AND = "OP_BIT_AND"           # &
    OP_BIT_OR = "OP_BIT_OR"             # |
    OP_BIT_XOR = "OP_BIT_XOR"           # ^
    OP_BIT_NOT = "OP_BIT_NOT"           # ~

    # Separators & Delimiters
    SEMICOLON = "SEMICOLON"             # ;
    COMMA = "COMMA"                     # ,
    DOT = "DOT"                         # .
    COLON = "COLON"                     # :
    LPAREN = "LPAREN"                   # (
    RPAREN = "RPAREN"                   # )
    LBRACE = "LBRACE"                   # {
    RBRACE = "RBRACE"                   # }
    LBRACKET = "LBRACKET"               # [
    RBRACKET = "RBRACKET"               # ]

    # Python Indentation Tokens
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    NEWLINE = "NEWLINE"

    # Preprocessor & Annotations
    PREPROCESSOR = "PREPROCESSOR"       # #include, #define
    ANNOTATION = "ANNOTATION"           # @Override

    # Comments
    COMMENT = "COMMENT"

    # Special / EOF
    EOF = "EOF"
    UNKNOWN = "UNKNOWN"

    def category(self) -> str:
        """Returns the high-level category of the token for statistical reporting."""
        name = self.name
        if name.startswith("KEYWORD"):
            return "Keyword"
        if name in ("INT_LITERAL", "FLOAT_LITERAL", "STRING_LITERAL", "CHAR_LITERAL"):
            return "Literal"
        if name == "IDENTIFIER":
            return "Identifier"
        if name.startswith("OP_"):
            return "Operator"
        if name in ("SEMICOLON", "COMMA", "DOT", "COLON", "LPAREN", "RPAREN", "LBRACE", "RBRACE", "LBRACKET", "RBRACKET"):
            return "Separator"
        if name in ("INDENT", "DEDENT", "NEWLINE"):
            return "Indentation"
        if name in ("PREPROCESSOR", "ANNOTATION"):
            return "Directive"
        if name == "COMMENT":
            return "Comment"
        return "Special"


# Backward-compatible KEYWORDS map for original C subset
KEYWORDS = {
    "int": TokenType.KEYWORD_INT,
    "float": TokenType.KEYWORD_FLOAT,
    "print": TokenType.KEYWORD_PRINT,
}

# Full C Keywords
C_KEYWORDS: Dict[str, TokenType] = {
    "int": TokenType.KEYWORD_INT,
    "float": TokenType.KEYWORD_FLOAT,
    "char": TokenType.KEYWORD_CHAR,
    "double": TokenType.KEYWORD_DOUBLE,
    "void": TokenType.KEYWORD_VOID,
    "if": TokenType.KEYWORD_IF,
    "else": TokenType.KEYWORD_ELSE,
    "for": TokenType.KEYWORD_FOR,
    "while": TokenType.KEYWORD_WHILE,
    "return": TokenType.KEYWORD_RETURN,
    "switch": TokenType.KEYWORD_SWITCH,
    "case": TokenType.KEYWORD_CASE,
    "break": TokenType.KEYWORD_BREAK,
    "continue": TokenType.KEYWORD_CONTINUE,
    "struct": TokenType.KEYWORD_STRUCT,
    "print": TokenType.KEYWORD_PRINT,  # preserved for compatibility
}

# Full Python Keywords
PYTHON_KEYWORDS: Dict[str, TokenType] = {
    "def": TokenType.KEYWORD_DEF,
    "class": TokenType.KEYWORD_CLASS,
    "if": TokenType.KEYWORD_IF,
    "elif": TokenType.KEYWORD_ELIF,
    "else": TokenType.KEYWORD_ELSE,
    "for": TokenType.KEYWORD_FOR,
    "while": TokenType.KEYWORD_WHILE,
    "return": TokenType.KEYWORD_RETURN,
    "import": TokenType.KEYWORD_IMPORT,
    "from": TokenType.KEYWORD_FROM,
    "try": TokenType.KEYWORD_TRY,
    "except": TokenType.KEYWORD_EXCEPT,
    "finally": TokenType.KEYWORD_FINALLY,
    "with": TokenType.KEYWORD_WITH,
    "as": TokenType.KEYWORD_AS,
    "pass": TokenType.KEYWORD_PASS,
    "break": TokenType.KEYWORD_BREAK,
    "continue": TokenType.KEYWORD_CONTINUE,
    "and": TokenType.KEYWORD_AND,
    "or": TokenType.KEYWORD_OR,
    "not": TokenType.KEYWORD_NOT,
    "in": TokenType.KEYWORD_IN,
    "is": TokenType.KEYWORD_IS,
    "True": TokenType.KEYWORD_TRUE,
    "False": TokenType.KEYWORD_FALSE,
    "None": TokenType.KEYWORD_NONE,
}

# Full Java Keywords
JAVA_KEYWORDS: Dict[str, TokenType] = {
    "class": TokenType.KEYWORD_CLASS,
    "public": TokenType.KEYWORD_PUBLIC,
    "private": TokenType.KEYWORD_PRIVATE,
    "protected": TokenType.KEYWORD_PROTECTED,
    "static": TokenType.KEYWORD_STATIC,
    "void": TokenType.KEYWORD_VOID,
    "int": TokenType.KEYWORD_INT,
    "double": TokenType.KEYWORD_DOUBLE,
    "float": TokenType.KEYWORD_FLOAT,
    "char": TokenType.KEYWORD_CHAR,
    "boolean": TokenType.KEYWORD_BOOLEAN,
    "String": TokenType.KEYWORD_STRING,
    "if": TokenType.KEYWORD_IF,
    "else": TokenType.KEYWORD_ELSE,
    "for": TokenType.KEYWORD_FOR,
    "while": TokenType.KEYWORD_WHILE,
    "return": TokenType.KEYWORD_RETURN,
    "new": TokenType.KEYWORD_NEW,
    "this": TokenType.KEYWORD_THIS,
    "extends": TokenType.KEYWORD_EXTENDS,
    "implements": TokenType.KEYWORD_IMPLEMENTS,
    "try": TokenType.KEYWORD_TRY,
    "catch": TokenType.KEYWORD_CATCH,
    "finally": TokenType.KEYWORD_FINALLY,
    "import": TokenType.KEYWORD_IMPORT,
    "package": TokenType.KEYWORD_PACKAGE,
    "true": TokenType.KEYWORD_TRUE,
    "false": TokenType.KEYWORD_FALSE,
    "null": TokenType.KEYWORD_NULL,
    "break": TokenType.KEYWORD_BREAK,
    "continue": TokenType.KEYWORD_CONTINUE,
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
        cat = self.token_type.category() if hasattr(self.token_type, "category") else "Token"
        tt_val = self.token_type.value if hasattr(self.token_type, "value") else str(self.token_type)
        return {
            "token_type": tt_val,
            "category": cat,
            "lexeme": self.lexeme,
            "line": self.line,
            "column": self.column,
            "value": self.value,
        }

    def __repr__(self) -> str:
        tt_name = self.token_type.name if hasattr(self.token_type, "name") else str(self.token_type)
        return f"Token({tt_name}, '{self.lexeme}', Ln {self.line}, Col {self.column})"
