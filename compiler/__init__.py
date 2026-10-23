"""
Smart Lexical Analyzer & Syntax Checker Compiler Package.
"""

from .tokens import Token, TokenType, KEYWORDS
from .lexer import Lexer
from .ast_nodes import (
    ASTNode, ProgramNode, StatementNode, DeclarationNode,
    AssignmentNode, PrintStatementNode, ExpressionNode,
    BinaryOpNode, UnaryOpNode, NumberLiteralNode, VariableNode
)
from .parser import Parser
from .semantic import SemanticAnalyzer, SymbolTable, Symbol
from .tac import TACGenerator, TACInstruction
from .diagnostics import Diagnostic, DiagnosticPhase, CompilationResult
from .pipeline import compile_source

__all__ = [
    "Token",
    "TokenType",
    "KEYWORDS",
    "Lexer",
    "Parser",
    "ASTNode",
    "ProgramNode",
    "StatementNode",
    "DeclarationNode",
    "AssignmentNode",
    "PrintStatementNode",
    "ExpressionNode",
    "BinaryOpNode",
    "UnaryOpNode",
    "NumberLiteralNode",
    "VariableNode",
    "SemanticAnalyzer",
    "SymbolTable",
    "Symbol",
    "TACGenerator",
    "TACInstruction",
    "Diagnostic",
    "DiagnosticPhase",
    "CompilationResult",
    "compile_source",
]

