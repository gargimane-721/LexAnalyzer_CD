"""
Abstract Syntax Tree (AST) node definitions for C, Python, and Java.
Provides structured tree representations while preserving all original nodes.
"""

from dataclasses import dataclass, field
from typing import List, Union, Optional, Any, Dict


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
    value: Union[int, float, complex] = 0
    raw: str = ""
    num_type: str = "int"

    def to_dict(self) -> dict:
        return {
            "node_type": "NumberLiteral",
            "value": str(self.value) if isinstance(self.value, complex) else self.value,
            "raw": self.raw,
            "num_type": self.num_type,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class StringLiteralNode(ExpressionNode):
    """Represents a string literal."""
    value: str = ""

    def to_dict(self) -> dict:
        return {
            "node_type": "StringLiteral",
            "value": self.value,
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
    """Represents a binary arithmetic, relational, or logical operation."""
    left: ExpressionNode = field(default_factory=lambda: ExpressionNode())
    operator: str = ""
    right: ExpressionNode = field(default_factory=lambda: ExpressionNode())

    def to_dict(self) -> dict:
        return {
            "node_type": "BinaryOp",
            "operator": self.operator,
            "left": self.left.to_dict() if hasattr(self.left, "to_dict") else None,
            "right": self.right.to_dict() if hasattr(self.right, "to_dict") else None,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class UnaryOpNode(ExpressionNode):
    """Represents a unary operation (+, -, !)."""
    operator: str = ""
    operand: ExpressionNode = field(default_factory=lambda: ExpressionNode())

    def to_dict(self) -> dict:
        return {
            "node_type": "UnaryOp",
            "operator": self.operator,
            "operand": self.operand.to_dict() if hasattr(self.operand, "to_dict") else None,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class FunctionCallNode(ExpressionNode):
    """Represents a function or method call."""
    callee: str = ""
    arguments: List[ExpressionNode] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "node_type": "FunctionCall",
            "callee": self.callee,
            "arguments": [a.to_dict() if hasattr(a, "to_dict") else str(a) for a in self.arguments],
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
    expression: Optional[ExpressionNode] = None

    def to_dict(self) -> dict:
        return {
            "node_type": "Declaration",
            "var_type": self.var_type,
            "identifier": self.identifier,
            "expression": self.expression.to_dict() if hasattr(self.expression, "to_dict") else None,
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
            "expression": self.expression.to_dict() if hasattr(self.expression, "to_dict") else None,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class PrintStatementNode(StatementNode):
    """Represents a print statement: e.g. print(c); or System.out.println(c);"""
    expression: ExpressionNode = field(default_factory=lambda: ExpressionNode())

    def to_dict(self) -> dict:
        return {
            "node_type": "PrintStatement",
            "expression": self.expression.to_dict() if hasattr(self.expression, "to_dict") else None,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class ReturnNode(StatementNode):
    """Represents a return statement: e.g. return 0;"""
    expression: Optional[ExpressionNode] = None

    def to_dict(self) -> dict:
        return {
            "node_type": "ReturnStatement",
            "expression": self.expression.to_dict() if hasattr(self.expression, "to_dict") else None,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class BlockNode(StatementNode):
    """Represents a block of statements enclosed in braces { ... }."""
    statements: List[StatementNode] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "node_type": "Block",
            "statements": [s.to_dict() if hasattr(s, "to_dict") else str(s) for s in self.statements],
            "line": self.line,
            "column": self.column,
        }


@dataclass
class IfNode(StatementNode):
    """Represents an if / else statement."""
    condition: ExpressionNode = field(default_factory=lambda: ExpressionNode())
    then_branch: StatementNode = field(default_factory=lambda: StatementNode())
    else_branch: Optional[StatementNode] = None

    def to_dict(self) -> dict:
        return {
            "node_type": "IfStatement",
            "condition": self.condition.to_dict() if hasattr(self.condition, "to_dict") else None,
            "then_branch": self.then_branch.to_dict() if hasattr(self.then_branch, "to_dict") else None,
            "else_branch": self.else_branch.to_dict() if hasattr(self.else_branch, "to_dict") else None,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class WhileNode(StatementNode):
    """Represents a while loop."""
    condition: ExpressionNode = field(default_factory=lambda: ExpressionNode())
    body: StatementNode = field(default_factory=lambda: StatementNode())

    def to_dict(self) -> dict:
        return {
            "node_type": "WhileStatement",
            "condition": self.condition.to_dict() if hasattr(self.condition, "to_dict") else None,
            "body": self.body.to_dict() if hasattr(self.body, "to_dict") else None,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class FunctionDefNode(StatementNode):
    """Represents a function definition: e.g. int main() { ... }"""
    return_type: str = "void"
    name: str = ""
    parameters: List[str] = field(default_factory=list)
    body: Optional[BlockNode] = None

    def to_dict(self) -> dict:
        return {
            "node_type": "FunctionDef",
            "return_type": self.return_type,
            "name": self.name,
            "parameters": self.parameters,
            "body": self.body.to_dict() if self.body else None,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class PreprocessorNode(StatementNode):
    """Represents a C preprocessor directive: e.g. #include <stdio.h>"""
    directive: str = ""

    def to_dict(self) -> dict:
        return {
            "node_type": "PreprocessorDirective",
            "directive": self.directive,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class ClassDefNode(StatementNode):
    """Represents an object-oriented class definition (Java / Python)."""
    name: str = ""
    modifiers: List[str] = field(default_factory=list)
    super_classes: List[str] = field(default_factory=list)
    members: List[StatementNode] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "node_type": "ClassDef",
            "name": self.name,
            "modifiers": self.modifiers,
            "super_classes": self.super_classes,
            "members": [m.to_dict() if hasattr(m, "to_dict") else str(m) for m in self.members],
            "line": self.line,
            "column": self.column,
        }


@dataclass
class GenericNode(ASTNode):
    """Generic AST node for parsed language constructs."""
    name: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    children: List[ASTNode] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "node_type": self.name,
            "details": self.details,
            "children": [c.to_dict() if hasattr(c, "to_dict") else str(c) for c in self.children],
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
            "statements": [stmt.to_dict() if hasattr(stmt, "to_dict") else str(stmt) for stmt in self.statements],
            "line": self.line,
            "column": self.column,
        }
