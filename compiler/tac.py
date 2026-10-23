"""
Intermediate Code Generator (Three-Address Code / 3AC).
Transforms the parsed AST into linearized three-address code instructions using temporary variables.
"""

from typing import List, Tuple
from .ast_nodes import (
    ProgramNode, StatementNode, DeclarationNode, AssignmentNode,
    PrintStatementNode, ExpressionNode, BinaryOpNode, UnaryOpNode,
    NumberLiteralNode, VariableNode
)


class TACInstruction:
    """Represents a single Three-Address Code instruction."""

    def __init__(self, op: str, arg1: str = "", arg2: str = "", result: str = "", comment: str = ""):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result
        self.comment = comment

    def __str__(self) -> str:
        if self.op == "ASSIGN":
            s = f"{self.result} = {self.arg1}"
        elif self.op in ("+", "-", "*", "/"):
            s = f"{self.result} = {self.arg1} {self.op} {self.arg2}"
        elif self.op == "UNARY_MINUS":
            s = f"{self.result} = -{self.arg1}"
        elif self.op == "UNARY_PLUS":
            s = f"{self.result} = +{self.arg1}"
        elif self.op == "PRINT":
            s = f"print {self.arg1}"
        else:
            s = f"{self.result} = {self.op} {self.arg1} {self.arg2}".strip()

        if self.comment:
            s = f"{s:<30} # {self.comment}"
        return s


class TACGenerator:
    """Generates 3AC from an AST ProgramNode."""

    def __init__(self):
        self.temp_counter = 0
        self.instructions: List[TACInstruction] = []

    def new_temp(self) -> str:
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def generate(self, program: ProgramNode) -> List[str]:
        """Translates the AST into a list of TAC instruction strings."""
        self.temp_counter = 0
        self.instructions = []

        if not program:
            return []

        for stmt in program.statements:
            self.visit_statement(stmt)

        return [str(inst) for inst in self.instructions]

    def visit_statement(self, stmt: StatementNode) -> None:
        if isinstance(stmt, DeclarationNode):
            addr = self.visit_expression(stmt.expression)
            self.instructions.append(
                TACInstruction(
                    op="ASSIGN",
                    arg1=addr,
                    result=stmt.identifier,
                    comment=f"declare {stmt.var_type} {stmt.identifier}"
                )
            )

        elif isinstance(stmt, AssignmentNode):
            addr = self.visit_expression(stmt.expression)
            self.instructions.append(
                TACInstruction(
                    op="ASSIGN",
                    arg1=addr,
                    result=stmt.identifier,
                    comment=f"assign to {stmt.identifier}"
                )
            )

        elif isinstance(stmt, PrintStatementNode):
            addr = self.visit_expression(stmt.expression)
            self.instructions.append(
                TACInstruction(
                    op="PRINT",
                    arg1=addr,
                    comment="output value"
                )
            )

    def visit_expression(self, expr: ExpressionNode) -> str:
        """Emits TAC for expression and returns the address (variable or literal) holding the result."""
        if isinstance(expr, NumberLiteralNode):
            return str(expr.value)

        if isinstance(expr, VariableNode):
            return expr.name

        if isinstance(expr, UnaryOpNode):
            operand_addr = self.visit_expression(expr.operand)
            temp = self.new_temp()
            op = "UNARY_MINUS" if expr.operator == "-" else "UNARY_PLUS"
            self.instructions.append(
                TACInstruction(op=op, arg1=operand_addr, result=temp)
            )
            return temp

        if isinstance(expr, BinaryOpNode):
            left_addr = self.visit_expression(expr.left)
            right_addr = self.visit_expression(expr.right)
            temp = self.new_temp()
            self.instructions.append(
                TACInstruction(
                    op=expr.operator,
                    arg1=left_addr,
                    arg2=right_addr,
                    result=temp
                )
            )
            return temp

        return ""

