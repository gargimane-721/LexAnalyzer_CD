"""
Tests for full C language Lexer, Parser, and Pipeline integration.
"""

import pytest
from compiler.lexers.c_lexer import CLexer
from compiler.parsers.c_parser import CParser
from compiler.tokens import TokenType
from compiler.pipeline import compile_source


def test_c_full_program_lexing():
    source = """
    #include <stdio.h>

    int main() {
        int x = 10;
        int y = 20;
        printf("%d", x + y);
        return 0;
    }
    """
    lexer = CLexer(source)
    tokens, diags = lexer.tokenize()

    assert len(diags) == 0
    types = [t.token_type for t in tokens if t.token_type != TokenType.EOF]
    assert TokenType.PREPROCESSOR in types
    assert TokenType.KEYWORD_INT in types
    assert TokenType.KEYWORD_RETURN in types
    assert TokenType.STRING_LITERAL in types
    assert TokenType.LBRACE in types
    assert TokenType.RBRACE in types


def test_c_full_program_parsing():
    source = """
    #include <stdio.h>

    int main() {
        int x = 10;
        int y = 20;
        printf("%d", x + y);
        return 0;
    }
    """
    lexer = CLexer(source)
    tokens, _ = lexer.tokenize()
    parser = CParser(tokens, source_code=source)
    ast, diags = parser.parse()

    assert len(diags) == 0
    assert len(ast.statements) == 2  # PreprocessorNode and FunctionDefNode (main)


def test_c_missing_semicolon_error():
    source = """
    int main() {
        int x = 10
        return 0;
    }
    """
    res = compile_source(source, language="c")
    assert res.status == "FAILED"
    sem_errs = [d for d in res.diagnostics if d.error_code == "SYN001"]
    assert len(sem_errs) >= 1
    assert "Expected ';'" in sem_errs[0].message


def test_c_unmatched_braces_error():
    source = """
    int main() {
        int x = 10;
        return 0;
    """
    res = compile_source(source, language="c")
    assert res.status == "FAILED"
    brace_errs = [d for d in res.diagnostics if d.error_code == "SYN002"]
    assert len(brace_errs) >= 1


def test_c_unterminated_string_error():
    source = 'char* s = "unterminated string;'
    lexer = CLexer(source)
    tokens, diags = lexer.tokenize()
    assert any(d.error_code == "LEX004" for d in diags)


def test_c_comments_handling():
    source = """
    // Single line comment
    /* Multi
       Line
       Comment */
    int x = 5;
    """
    lexer = CLexer(source)
    tokens, diags = lexer.tokenize()
    assert len(diags) == 0
    lexemes = [t.lexeme for t in tokens if t.token_type != TokenType.EOF]
    assert lexemes == ["int", "x", "=", "5", ";"]

