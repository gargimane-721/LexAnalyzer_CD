"""
Unit tests for the Semantic Analyzer and Symbol Table.
"""

import pytest
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic import SemanticAnalyzer


def run_semantics(source: str):
    lexer = Lexer(source)
    tokens, _ = lexer.tokenize()
    parser = Parser(tokens)
    ast, _ = parser.parse()
    analyzer = SemanticAnalyzer()
    sym_table, diags = analyzer.analyze(ast)
    return sym_table, diags


def test_symbol_table_population():
    source = "int a = 10; float b = 2.5;"
    sym_table, diags = run_semantics(source)

    assert len(diags) == 0
    assert sym_table.lookup("a") is not None
    assert sym_table.lookup("a").var_type == "int"
    assert sym_table.lookup("b") is not None
    assert sym_table.lookup("b").var_type == "float"


def test_duplicate_declaration():
    source = "int a = 10; float a = 20.0;"
    sym_table, diags = run_semantics(source)

    dup_errors = [d for d in diags if d.error_code == "SEM001"]
    assert len(dup_errors) == 1
    assert "Duplicate declaration of variable 'a'" in dup_errors[0].message


def test_undeclared_variable_in_assignment():
    source = "x = 42;"
    sym_table, diags = run_semantics(source)

    und_errors = [d for d in diags if d.error_code == "SEM002"]
    assert len(und_errors) == 1
    assert "Undeclared variable 'x'" in und_errors[0].message


def test_undeclared_variable_in_expression():
    source = "int a = 10; int b = a + mysteryVar;"
    sym_table, diags = run_semantics(source)

    und_errors = [d for d in diags if d.error_code == "SEM002"]
    assert len(und_errors) == 1
    assert "mysteryVar" in und_errors[0].message


def test_static_division_by_zero():
    source = "int a = 10; int b = a / 0;"
    sym_table, diags = run_semantics(source)

    div_errors = [d for d in diags if d.error_code == "SEM004"]
    assert len(div_errors) == 1
    assert "Static division by zero" in div_errors[0].message

