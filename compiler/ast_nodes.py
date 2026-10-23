"""
Abstract Syntax Tree (AST) node definitions for the C-like source language.
Provides structured tree representation of parsed programs.
"""

from dataclasses import dataclass, field
from typing import List, Union, Optional, Any


@dataclass
class ASTNode:
    """Base class for all Abstract Syntax Tree nodes."""
    line: int = 0
    column: int = 0

    def to_dict(self) -> dict:
        raise NotImplementedError


@dataclass
class ExpressionNode(ASTNode):
    """Base class for all expression nodes."""
    inferred_type: Optional[str] = None


@dataclass
class NumberLiteralNode(ExpressionNode):
    """Represents an integer or float literal."""
    value: Union[int, float] = 0
    raw: str = ""
    num_type: str = "int"

    def to_dict(self) -> dict:
        return {
            "node_type": "NumberLiteral",
            "value": self.value,
            "raw": self.raw,
            "num_type": self.num_type,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class VariableNode(ExpressionNode):
    """Represents a variable identifier usage in an expression."""
    name: str = ""

    def to_dict(self) -> dict:
        return {
            "node_type": "Variable",
            "name": self.name,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class BinaryOpNode(ExpressionNode):
    """Represents a binary arithmetic operation (+, -, *, /)."""
    left: ExpressionNode = field(default_factory=lambda: ExpressionNode())
    operator: str = ""
    right: ExpressionNode = field(default_factory=lambda: ExpressionNode())

    def to_dict(self) -> dict:
        return {
            "node_type": "BinaryOp",
            "operator": self.operator,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class UnaryOpNode(ExpressionNode):
    """Represents a unary operation (+, -)."""
    operator: str = ""
    operand: ExpressionNode = field(default_factory=lambda: ExpressionNode())

    def to_dict(self) -> dict:
        return {
            "node_type": "UnaryOp",
            "operator": self.operator,
            "operand": self.operand.to_dict() if self.operand else None,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class StatementNode(ASTNode):
    """Base class for program statements."""
    pass


@dataclass
class DeclarationNode(StatementNode):
    """Represents a variable declaration: e.g. int a = 10;"""
    var_type: str = ""
    identifier: str = ""
    expression: ExpressionNode = field(default_factory=lambda: ExpressionNode())

    def to_dict(self) -> dict:
        return {
            "node_type": "Declaration",
            "var_type": self.var_type,
            "identifier": self.identifier,
            "expression": self.expression.to_dict() if self.expression else None,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class AssignmentNode(StatementNode):
    """Represents a variable assignment: e.g. a = b + 2;"""
    identifier: str = ""
    expression: ExpressionNode = field(default_factory=lambda: ExpressionNode())

    def to_dict(self) -> dict:
        return {
            "node_type": "Assignment",
            "identifier": self.identifier,
            "expression": self.expression.to_dict() if self.expression else None,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class PrintStatementNode(StatementNode):
    """Represents a print statement: e.g. print(c);"""
    expression: ExpressionNode = field(default_factory=lambda: ExpressionNode())

    def to_dict(self) -> dict:
        return {
            "node_type": "PrintStatement",
            "expression": self.expression.to_dict() if self.expression else None,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class ProgramNode(ASTNode):
    """Root node of the Abstract Syntax Tree."""
    statements: List[StatementNode] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "node_type": "Program",
            "statements": [stmt.to_dict() for stmt in self.statements],
            "line": self.line,
            "column": self.column,
        }

