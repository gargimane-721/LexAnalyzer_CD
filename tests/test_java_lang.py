"""
Tests for Java language Lexer, Parser, and Pipeline integration.
"""

import pytest
from compiler.lexers.java_lexer import JavaLexer
from compiler.parsers.java_parser import JavaParser
from compiler.tokens import TokenType
from compiler.pipeline import compile_source


def test_java_program_lexing():
    source = """
    public class Main {
        public static void main(String[] args) {
            int x = 10;
            int y = 20;
            System.out.println(x + y);
        }
    }
    """
    lexer = JavaLexer(source)
    tokens, diags = lexer.tokenize()

    assert len(diags) == 0
    types = [t.token_type for t in tokens if t.token_type != TokenType.EOF]
    assert TokenType.KEYWORD_PUBLIC in types
    assert TokenType.KEYWORD_CLASS in types
    assert TokenType.KEYWORD_STATIC in types
    assert TokenType.KEYWORD_VOID in types
    assert TokenType.KEYWORD_INT in types
    assert TokenType.LBRACE in types
    assert TokenType.RBRACE in types


def test_java_program_parsing():
    source = """
    public class Main {
        public static void main(String[] args) {
            int x = 10;
            int y = 20;
            System.out.println(x + y);
        }
    }
    """
    res = compile_source(source, language="java")
    assert res.status == "SUCCESS"
    assert res.error_count == 0
    assert res.ast is not None


def test_java_missing_semicolon_error():
    source = """
    public class Main {
        public static void main(String[] args) {
            int x = 10
            int y = 20;
        }
    }
    """
    res = compile_source(source, language="java")
    assert res.status == "FAILED"
    assert any("SYN001" in d.error_code or "semicolon" in d.message.lower() for d in res.diagnostics)


def test_java_unmatched_braces_error():
    source = """
    public class Main {
        public static void main(String[] args) {
            int x = 10;
        }
    """
    res = compile_source(source, language="java")
    assert res.status == "FAILED"
    assert any("SYN_JAVA_002" in d.error_code for d in res.diagnostics)


def test_java_annotations_and_comments():
    source = """
    // Single line
    /* Multi line */
    /** Javadoc */
    @Override
    public class Test {
    }
    """
    lexer = JavaLexer(source)
    tokens, diags = lexer.tokenize()
    assert len(diags) == 0
    types = [t.token_type for t in tokens if t.token_type != TokenType.EOF]
    assert TokenType.ANNOTATION in types
    assert TokenType.KEYWORD_CLASS in types

