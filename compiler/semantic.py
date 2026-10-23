"""
Semantic Analyzer and Symbol Table manager.
Enforces variable declaration rules, type checking, static division-by-zero detection,
and variable initialization tracking.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from .ast_nodes import (
    ProgramNode, StatementNode, DeclarationNode, AssignmentNode,
    PrintStatementNode, ExpressionNode, BinaryOpNode, UnaryOpNode,
    NumberLiteralNode, VariableNode
)
from .diagnostics import Diagnostic, DiagnosticPhase


@dataclass
class Symbol:
    """Represents an entry in the compiler's symbol table."""
    name: str
    var_type: str        # 'int' or 'float'
    line_declared: int
    column_declared: int
    is_initialized: bool = True
    last_assigned_line: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.var_type,
            "line_declared": self.line_declared,
            "column_declared": self.column_declared,
            "is_initialized": self.is_initialized,
            "last_assigned_line": self.last_assigned_line or self.line_declared,
        }


class SymbolTable:
    """Stores and queries declared identifiers."""

    def __init__(self):
        self.symbols: Dict[str, Symbol] = {}

    def insert(self, symbol: Symbol) -> bool:
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True

    def lookup(self, name: str) -> Optional[Symbol]:
        return self.symbols.get(name)

    def all_symbols(self) -> List[Symbol]:
        return list(self.symbols.values())

    def to_list(self) -> List[dict]:
        return [s.to_dict() for s in self.symbols.values()]


class SemanticAnalyzer:
    """Walks the AST, checks semantic rules, and builds the symbol table."""

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.diagnostics: List[Diagnostic] = []

    def analyze(self, program: ProgramNode) -> Tuple[SymbolTable, List[Diagnostic]]:
        """Performs static semantic checks on the program AST."""
        self.symbol_table = SymbolTable()
        self.diagnostics = []

        if not program:
            return self.symbol_table, self.diagnostics

        for stmt in program.statements:
            self.visit_statement(stmt)

        return self.symbol_table, self.diagnostics

    def visit_statement(self, stmt: StatementNode) -> None:
        if isinstance(stmt, DeclarationNode):
            self.visit_declaration(stmt)
        elif isinstance(stmt, AssignmentNode):
            self.visit_assignment(stmt)
        elif isinstance(stmt, PrintStatementNode):
            self.visit_print_statement(stmt)

    def visit_declaration(self, node: DeclarationNode) -> None:
        # Check duplicate declaration
        existing = self.symbol_table.lookup(node.identifier)
        if existing:
            self.diagnostics.append(
                Diagnostic(
                    phase=DiagnosticPhase.SEMANTIC,
                    error_code="SEM001",
                    message=f"Duplicate declaration of variable '{node.identifier}'. Previously declared at line {existing.line_declared}.",
                    line=node.line,
                    column=node.column,
                    suggestion="Remove duplicate declaration or use a distinct variable name."
                )
            )
            return

        # Analyze the right-hand side expression
        expr_type = self.visit_expression(node.expression)

        # Basic type checking / warning
        if node.var_type == "int" and expr_type == "float":
            self.diagnostics.append(
                Diagnostic(
                    phase=DiagnosticPhase.SEMANTIC,
                    error_code="SEM005",
                    message=f"Type warning: Assigning 'float' expression to 'int' variable '{node.identifier}' causes precision loss.",
                    line=node.line,
                    column=node.column,
                    suggestion=f"Declare '{node.identifier}' as 'float' or round the value."
                )
            )

        # Register new symbol
        sym = Symbol(
            name=node.identifier,
            var_type=node.var_type,
            line_declared=node.line,
            column_declared=node.column,
            is_initialized=True,
            last_assigned_line=node.line
        )
        self.symbol_table.insert(sym)

    def visit_assignment(self, node: AssignmentNode) -> None:
        sym = self.symbol_table.lookup(node.identifier)
        if not sym:
            self.diagnostics.append(
                Diagnostic(
                    phase=DiagnosticPhase.SEMANTIC,
                    error_code="SEM002",
                    message=f"Undeclared variable '{node.identifier}'. Cannot assign value before declaration.",
                    line=node.line,
                    column=node.column,
                    suggestion=f"Declare variable first: e.g. 'int {node.identifier} = 0;' or 'float {node.identifier} = 0.0;'"
                )
            )
        else:
            sym.is_initialized = True
            sym.last_assigned_line = node.line

        expr_type = self.visit_expression(node.expression)
        if sym and sym.var_type == "int" and expr_type == "float":
            self.diagnostics.append(
                Diagnostic(
                    phase=DiagnosticPhase.SEMANTIC,
                    error_code="SEM005",
                    message=f"Type warning: Assigning 'float' value to 'int' variable '{node.identifier}' causes precision loss.",
                    line=node.line,
                    column=node.column,
                    suggestion=f"Declare '{node.identifier}' as 'float' if fractional values are required."
                )
            )

    def visit_print_statement(self, node: PrintStatementNode) -> None:
        self.visit_expression(node.expression)

    def visit_expression(self, expr: ExpressionNode) -> Optional[str]:
        """Evaluates expression semantics, returns inferred type ('int' or 'float')."""
        if not expr:
            return None

        if isinstance(expr, NumberLiteralNode):
            expr.inferred_type = expr.num_type
            return expr.num_type

        if isinstance(expr, VariableNode):
            sym = self.symbol_table.lookup(expr.name)
            if not sym:
                self.diagnostics.append(
                    Diagnostic(
                        phase=DiagnosticPhase.SEMANTIC,
                        error_code="SEM002",
                        message=f"Use of undeclared variable '{expr.name}' in expression.",
                        line=expr.line,
                        column=expr.column,
                        suggestion=f"Declare '{expr.name}' with 'int' or 'float' before using it."
                    )
                )
                return "int"  # Fallback assumption
            if not sym.is_initialized:
                self.diagnostics.append(
                    Diagnostic(
                        phase=DiagnosticPhase.SEMANTIC,
                        error_code="SEM003",
                        message=f"Variable '{expr.name}' is used before being initialized.",
                        line=expr.line,
                        column=expr.column,
                        suggestion=f"Initialize '{expr.name}' with a value before reading it."
                    )
                )
            expr.inferred_type = sym.var_type
            return sym.var_type

        if isinstance(expr, UnaryOpNode):
            t = self.visit_expression(expr.operand)
            expr.inferred_type = t
            return t

        if isinstance(expr, BinaryOpNode):
            left_type = self.visit_expression(expr.left)
            right_type = self.visit_expression(expr.right)

            # Static division by zero check
            if expr.operator == "/":
                if isinstance(expr.right, NumberLiteralNode) and expr.right.value == 0:
                    self.diagnostics.append(
                        Diagnostic(
                            phase=DiagnosticPhase.SEMANTIC,
                            error_code="SEM004",
                            message="Static division by zero detected in expression.",
                            line=expr.line,
                            column=expr.column,
                            suggestion="Ensure divisor is non-zero to avoid division by zero runtime error."
                        )
                    )

            # Type promotion rule: float + int -> float
            result_type = "float" if "float" in (left_type, right_type) else "int"
            expr.inferred_type = result_type
            return result_type

        return None

