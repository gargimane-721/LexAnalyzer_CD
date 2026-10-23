"""
Unit tests for the Syntax Checker (Recursive-Descent Parser).
"""

import pytest
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.ast_nodes import (
    DeclarationNode, AssignmentNode, PrintStatementNode,
    BinaryOpNode, NumberLiteralNode, VariableNode
)


def parse_snippet(source: str):
    lexer = Lexer(source)
    tokens, lex_diags = lexer.tokenize()
    parser = Parser(tokens)
    ast, parse_diags = parser.parse()
    return ast, lex_diags + parse_diags


def test_valid_declarations():
    source = "int a = 10; float b = 5.5;"
    ast, diags = parse_snippet(source)

    assert len(diags) == 0
    assert len(ast.statements) == 2
    assert isinstance(ast.statements[0], DeclarationNode)
    assert ast.statements[0].var_type == "int"
    assert ast.statements[0].identifier == "a"
    assert isinstance(ast.statements[1], DeclarationNode)
    assert ast.statements[1].var_type == "float"
    assert ast.statements[1].identifier == "b"


def test_valid_assignment_and_print():
    source = "x = y + 5; print(x);"
    ast, diags = parse_snippet(source)

    assert len(diags) == 0
    assert len(ast.statements) == 2
    assert isinstance(ast.statements[0], AssignmentNode)
    assert ast.statements[0].identifier == "x"
    assert isinstance(ast.statements[1], PrintStatementNode)


def test_operator_precedence():
    # In a + b * 2, the root operator must be '+', with left = a, and right = (b * 2)
    source = "int c = a + b * 2;"
    ast, diags = parse_snippet(source)

    assert len(diags) == 0
    decl = ast.statements[0]
    expr = decl.expression
    assert isinstance(expr, BinaryOpNode)
    assert expr.operator == "+"
    assert isinstance(expr.left, VariableNode)
    assert expr.left.name == "a"
    assert isinstance(expr.right, BinaryOpNode)
    assert expr.right.operator == "*"
    assert expr.right.left.name == "b"
    assert expr.right.right.value == 2


def test_parentheses_override_precedence():
    # In (a + b) * 2, the root operator must be '*', with left = (a + b), and right = 2
    source = "int c = (a + b) * 2;"
    ast, diags = parse_snippet(source)

    assert len(diags) == 0
    decl = ast.statements[0]
    expr = decl.expression
    assert isinstance(expr, BinaryOpNode)
    assert expr.operator == "*"
    assert isinstance(expr.left, BinaryOpNode)
    assert expr.left.operator == "+"
    assert expr.right.value == 2


def test_missing_semicolon():
    source = "int a = 10\nint b = 20;"
    ast, diags = parse_snippet(source)

    # Parser should catch missing semicolon and still recover to parse second statement
    semicolon_errors = [d for d in diags if d.error_code == "SYN001"]
    assert len(semicolon_errors) >= 1
    assert "Expected ';'" in semicolon_errors[0].message


def test_unmatched_parenthesis():
    source = "int a = (10 + 20;"
    ast, diags = parse_snippet(source)

    paren_errors = [d for d in diags if d.error_code == "SYN002"]
    assert len(paren_errors) >= 1
    assert "Expected closing ')'" in paren_errors[0].message


def test_missing_identifier_in_declaration():
    source = "int = 10;"
    ast, diags = parse_snippet(source)

    ident_errors = [d for d in diags if d.error_code == "SYN003"]
    assert len(ident_errors) >= 1
    assert "Expected identifier after type" in ident_errors[0].message


def test_missing_equals_in_declaration():
    source = "int a 10;"
    ast, diags = parse_snippet(source)

    equals_errors = [d for d in diags if d.error_code == "SYN004"]
    assert len(equals_errors) >= 1
    assert "Expected '='" in equals_errors[0].message


def test_unexpected_token_in_expression():
    source = "int a = + ;"
    ast, diags = parse_snippet(source)

    expr_errors = [d for d in diags if d.error_code == "SYN005"]
    assert len(expr_errors) >= 1


def test_empty_input():
    source = ""
    ast, diags = parse_snippet(source)

    assert len(diags) == 0
    assert len(ast.statements) == 0

