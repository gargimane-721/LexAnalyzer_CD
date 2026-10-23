"""
Python Language Syntax Checker.
Validates Python syntax, significant indentation, and block structures using AST analysis
and provides beginner-friendly diagnostic reporting.
"""

import ast
from typing import List, Optional, Tuple, Any
from compiler.tokens import Token
from compiler.ast_nodes import (
    ProgramNode, StatementNode, GenericNode, AssignmentNode,
    FunctionDefNode, ClassDefNode, PrintStatementNode, ReturnNode
)
from compiler.diagnostics import Diagnostic, DiagnosticPhase
from .base_parser import BaseParser


class PythonParser(BaseParser):
    """Syntax validator and AST generator for Python code."""

    def __init__(self, tokens: List[Token], source_code: str = ""):
        super().__init__(tokens, source_code)

    def parse(self) -> Tuple[Optional[ProgramNode], List[Diagnostic]]:
        self.diagnostics = []

        if not self.source_code.strip():
            return ProgramNode(statements=[], line=1, column=1), self.diagnostics

        # 1. Check for lexical errors already recorded
        # If there are lexical indentation errors, log them
        # 2. Parse using Python's formal grammar parser
        try:
            py_ast = ast.parse(self.source_code)
            program_node = self._convert_py_ast(py_ast)
            return program_node, self.diagnostics
        except IndentationError as ie:
            line = ie.lineno or 1
            col = ie.offset or 1
            self.diagnostics.append(
                Diagnostic(
                    phase=DiagnosticPhase.SYNTAX,
                    error_code="SYN_PY_INDENT",
                    message=f"IndentationError: {ie.msg}",
                    line=line,
                    column=col,
                    suggestion="Ensure consistent 4-space indentation for all indented blocks under 'def', 'if', 'for', 'while', or 'class'."
                )
            )
            return None, self.diagnostics
        except SyntaxError as se:
            line = se.lineno or 1
            col = se.offset or 1
            msg = se.msg or "invalid syntax"

            # Beginner-friendly guidance mapping
            suggestion = "Review Python syntax rules for this line."
            if "expected ':'" in msg.lower():
                suggestion = "Add a colon ':' at the end of the header statement (e.g. 'if condition:', 'def func():', 'while x:')."
            elif "unmatched" in msg.lower() or "was never closed" in msg.lower():
                suggestion = "Check for missing closing parenthesis ')', bracket ']', brace '}', or quotation mark."
            elif "cannot assign to" in msg.lower():
                suggestion = "The left-hand side of an assignment must be a valid variable name."
            elif "invalid syntax" in msg.lower():
                suggestion = "Check for missing operators, misspelled keywords, or misplaced punctuation."

            self.diagnostics.append(
                Diagnostic(
                    phase=DiagnosticPhase.SYNTAX,
                    error_code="SYN_PY_SYNTAX",
                    message=f"SyntaxError: {msg}",
                    line=line,
                    column=col,
                    suggestion=suggestion
                )
            )
            return None, self.diagnostics
        except Exception as ex:
            self.diagnostics.append(
                Diagnostic(
                    phase=DiagnosticPhase.SYNTAX,
                    error_code="SYN_PY_ERROR",
                    message=f"Parse Error: {str(ex)}",
                    line=1,
                    column=1,
                    suggestion="Verify that source code adheres to valid Python 3 syntax."
                )
            )
            return None, self.diagnostics

    def _convert_py_ast(self, py_ast: ast.Module) -> ProgramNode:
        """Converts standard Python AST module into our unified ASTNode hierarchy."""
        statements: List[StatementNode] = []

        for item in py_ast.body:
            st = self._convert_stmt(item)
            if st:
                statements.append(st)

        return ProgramNode(statements=statements, line=1, column=1)

    def _convert_stmt(self, node: ast.AST) -> Optional[StatementNode]:
        line = getattr(node, "lineno", 1)
        col = getattr(node, "col_offset", 0) + 1

        if isinstance(node, ast.Assign):
            target = ast.unparse(node.targets[0]) if node.targets else "var"
            value_str = ast.unparse(node.value)
            return GenericNode(
                name="Assignment",
                details={"target": target, "value": value_str},
                line=line,
                column=col
            )

        elif isinstance(node, ast.FunctionDef):
            args = [a.arg for a in node.args.args]
            return FunctionDefNode(
                return_type="def",
                name=node.name,
                parameters=args,
                line=line,
                column=col
            )

        elif isinstance(node, ast.ClassDef):
            bases = [ast.unparse(b) for b in node.bases]
            return ClassDefNode(
                name=node.name,
                super_classes=bases,
                line=line,
                column=col
            )

        elif isinstance(node, ast.Return):
            val = ast.unparse(node.value) if node.value else "None"
            return GenericNode(
                name="ReturnStatement",
                details={"value": val},
                line=line,
                column=col
            )

        elif isinstance(node, ast.Expr):
            # Check for print(...) call
            if isinstance(node.value, ast.Call) and getattr(node.value.func, "id", None) == "print":
                args_str = ", ".join(ast.unparse(a) for a in node.value.args)
                return GenericNode(
                    name="PrintStatement",
                    details={"arguments": args_str},
                    line=line,
                    column=col
                )
            expr_str = ast.unparse(node.value)
            return GenericNode(
                name="ExpressionStatement",
                details={"expression": expr_str},
                line=line,
                column=col
            )

        elif isinstance(node, (ast.If, ast.While, ast.For)):
            type_name = type(node).__name__
            return GenericNode(
                name=f"{type_name}Statement",
                details={"summary": ast.unparse(node).splitlines()[0]},
                line=line,
                column=col
            )

        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            return GenericNode(
                name="ImportStatement",
                details={"module": ast.unparse(node)},
                line=line,
                column=col
            )

        return GenericNode(
            name=type(node).__name__,
            details={"code": ast.unparse(node) if hasattr(ast, "unparse") else ""},
            line=line,
            column=col
        )

