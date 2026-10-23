"""
Tests for Python language Lexer, Parser, and Pipeline integration.
"""

import pytest
from compiler.lexers.python_lexer import PythonLexer
from compiler.parsers.python_parser import PythonParser
from compiler.tokens import TokenType
from compiler.pipeline import compile_source


def test_python_program_lexing():
    source = """
x = 10
y = 20
print(x + y)
"""
    lexer = PythonLexer(source)
    tokens, diags = lexer.tokenize()

    assert len(diags) == 0
    types = [t.token_type for t in tokens if t.token_type != TokenType.EOF]
    assert TokenType.IDENTIFIER in types
    assert TokenType.OP_ASSIGN in types
    assert TokenType.INT_LITERAL in types
    assert TokenType.OP_PLUS in types
    assert TokenType.NEWLINE in types


def test_python_indentation_tokens():
    source = """
def greet():
    x = 10
    return x
"""
    lexer = PythonLexer(source)
    tokens, diags = lexer.tokenize()

    assert len(diags) == 0
    types = [t.token_type for t in tokens]
    assert TokenType.INDENT in types
    assert TokenType.DEDENT in types


def test_python_valid_syntax_parsing():
    source = """
x = 10
y = 20
print(x + y)
"""
    res = compile_source(source, language="python")
    assert res.status == "SUCCESS"
    assert res.is_success is True
    assert res.error_count == 0
    assert res.ast is not None


def test_python_invalid_indentation_error():
    source = """
def foo():
x = 10
"""
    res = compile_source(source, language="python")
    assert res.status == "FAILED"
    assert any("SYN_PY_INDENT" in d.error_code or "IndentationError" in d.message for d in res.diagnostics)


def test_python_missing_colon_error():
    source = """
if x > 10
    print(x)
"""
    res = compile_source(source, language="python")
    assert res.status == "FAILED"
    assert any("SYN_PY_SYNTAX" in d.error_code for d in res.diagnostics)


def test_python_comments_and_strings():
    source = """
# Leading comment
greeting = "Hello #world!" # inline comment
"""
    lexer = PythonLexer(source)
    tokens, diags = lexer.tokenize()
    assert len(diags) == 0
    strings = [t.value for t in tokens if t.token_type == TokenType.STRING_LITERAL]
    assert strings == ["Hello #world!"]

