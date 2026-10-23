"""
Unit tests for the Lexical Analyzer (Scanner).
"""

import pytest
from compiler.lexer import Lexer
from compiler.tokens import TokenType


def test_keywords_recognition():
    source = "int float print"
    lexer = Lexer(source)
    tokens, diags = lexer.tokenize()

    assert len(diags) == 0
    assert tokens[0].token_type == TokenType.KEYWORD_INT
    assert tokens[1].token_type == TokenType.KEYWORD_FLOAT
    assert tokens[2].token_type == TokenType.KEYWORD_PRINT
    assert tokens[3].token_type == TokenType.EOF


def test_keyword_vs_longer_identifier():
    # 'int' is a keyword, but 'integerValue' and 'internal' are identifiers
    source = "int integerValue internal"
    lexer = Lexer(source)
    tokens, diags = lexer.tokenize()

    assert len(diags) == 0
    assert tokens[0].token_type == TokenType.KEYWORD_INT
    assert tokens[1].token_type == TokenType.IDENTIFIER
    assert tokens[1].lexeme == "integerValue"
    assert tokens[2].token_type == TokenType.IDENTIFIER
    assert tokens[2].lexeme == "internal"


def test_integer_and_float_literals():
    source = "100 0 3.1415 0.05"
    lexer = Lexer(source)
    tokens, diags = lexer.tokenize()

    assert len(diags) == 0
    assert tokens[0].token_type == TokenType.INT_LITERAL
    assert tokens[0].value == 100
    assert tokens[1].token_type == TokenType.INT_LITERAL
    assert tokens[1].value == 0
    assert tokens[2].token_type == TokenType.FLOAT_LITERAL
    assert tokens[2].value == 3.1415
    assert tokens[3].token_type == TokenType.FLOAT_LITERAL
    assert tokens[3].value == 0.05


def test_operators_and_delimiters():
    source = "= + - * / ; ( )"
    lexer = Lexer(source)
    tokens, diags = lexer.tokenize()

    expected_types = [
        TokenType.OP_ASSIGN,
        TokenType.OP_PLUS,
        TokenType.OP_MINUS,
        TokenType.OP_MULTIPLY,
        TokenType.OP_DIVIDE,
        TokenType.SEMICOLON,
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.EOF
    ]
    actual_types = [t.token_type for t in tokens]
    assert actual_types == expected_types
    assert len(diags) == 0


def test_line_and_column_tracking():
    source = "int a = 10;\nfloat b = 2.5;"
    lexer = Lexer(source)
    tokens, diags = lexer.tokenize()

    assert len(diags) == 0
    # Line 1: int (col 1), a (col 5), = (col 7), 10 (col 9), ; (col 11)
    assert tokens[0].lexeme == "int"
    assert tokens[0].line == 1
    assert tokens[0].column == 1

    assert tokens[1].lexeme == "a"
    assert tokens[1].line == 1
    assert tokens[1].column == 5

    assert tokens[3].lexeme == "10"
    assert tokens[3].line == 1
    assert tokens[3].column == 9

    assert tokens[4].lexeme == ";"
    assert tokens[4].line == 1
    assert tokens[4].column == 11

    # Line 2: float (col 1), b (col 7), = (col 9), 2.5 (col 11), ; (col 14)
    assert tokens[5].lexeme == "float"
    assert tokens[5].line == 2
    assert tokens[5].column == 1


def test_comments_and_whitespace_ignored():
    source = """
    // Leading comment
    int x = 42; // Inline comment
    // Trailing comment
    """
    lexer = Lexer(source)
    tokens, diags = lexer.tokenize()

    assert len(diags) == 0
    lexemes = [t.lexeme for t in tokens[:-1]]  # exclude EOF
    assert lexemes == ["int", "x", "=", "42", ";"]


def test_unrecognized_characters_detection():
    source = "int a = 10 @ 5 # $;"
    lexer = Lexer(source)
    tokens, diags = lexer.tokenize()

    assert len(diags) == 3
    assert diags[0].error_code == "LEX001"
    assert "@" in diags[0].message
    assert diags[1].error_code == "LEX001"
    assert "#" in diags[1].message
    assert diags[2].error_code == "LEX001"
    assert "$" in diags[2].message


def test_malformed_numeric_literal():
    source = "float x = 12.34.56;"
    lexer = Lexer(source)
    tokens, diags = lexer.tokenize()

    assert len(diags) == 1
    assert diags[0].error_code == "LEX002"
    assert "12.34.56" in diags[0].message


def test_invalid_identifier_starting_with_digit():
    source = "int 99bottles = 99;"
    lexer = Lexer(source)
    tokens, diags = lexer.tokenize()

    assert len(diags) == 1
    assert diags[0].error_code == "LEX003"
    assert "99bottles" in diags[0].message

