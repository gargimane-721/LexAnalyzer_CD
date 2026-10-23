"""
Unit tests for the Intermediate Code Generator (Three-Address Code).
"""

import pytest
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.tac import TACGenerator


def generate_tac(source: str):
    lexer = Lexer(source)
    tokens, _ = lexer.tokenize()
    parser = Parser(tokens)
    ast, _ = parser.parse()
    gen = TACGenerator()
    return gen.generate(ast)


def test_tac_simple_declaration():
    source = "int a = 10;"
    instructions = generate_tac(source)

    assert len(instructions) == 1
    assert "a = 10" in instructions[0]


def test_tac_expression_precedence():
    # int c = a + b * 2;
    # Expected:
    # t1 = b * 2
    # t2 = a + t1
    # c = t2
    source = "int c = a + b * 2;"
    instructions = generate_tac(source)

    assert len(instructions) == 3
    assert "t1 = b * 2" in instructions[0]
    assert "t2 = a + t1" in instructions[1]
    assert "c = t2" in instructions[2]


def test_tac_parenthesized_expression():
    # int c = (a + b) * 2;
    # Expected:
    # t1 = a + b
    # t2 = t1 * 2
    # c = t2
    source = "int c = (a + b) * 2;"
    instructions = generate_tac(source)

    assert len(instructions) == 3
    assert "t1 = a + b" in instructions[0]
    assert "t2 = t1 * 2" in instructions[1]
    assert "c = t2" in instructions[2]


def test_tac_print_statement():
    source = "print(x * 5);"
    instructions = generate_tac(source)

    assert len(instructions) == 2
    assert "t1 = x * 5" in instructions[0]
    assert "print t1" in instructions[1]

