"""
Smart Multi-Language Compiler & Analyzer Package (C, Python, Java).
"""

from .tokens import Token, TokenType, KEYWORDS, C_KEYWORDS, PYTHON_KEYWORDS, JAVA_KEYWORDS
from .lexer import Lexer
from .lexers.c_lexer import CLexer
from .lexers.python_lexer import PythonLexer
from .lexers.java_lexer import JavaLexer
from .ast_nodes import (
    ASTNode, ProgramNode, StatementNode, DeclarationNode,
    AssignmentNode, PrintStatementNode, ExpressionNode,
    BinaryOpNode, UnaryOpNode, NumberLiteralNode, StringLiteralNode,
    VariableNode, FunctionCallNode, ReturnNode, BlockNode,
    IfNode, WhileNode, FunctionDefNode, ClassDefNode, PreprocessorNode, GenericNode
)
from .parser import Parser
from .parsers.c_parser import CParser
from .parsers.python_parser import PythonParser
from .parsers.java_parser import JavaParser
from .semantic import SemanticAnalyzer, SymbolTable, Symbol
from .tac import TACGenerator, TACInstruction
from .adapters.manager import ToolchainManager, toolchain_manager
from .adapters.base_adapter import BaseExecutionAdapter
from .adapters.c_adapter import CExecutionAdapter
from .adapters.python_adapter import PythonExecutionAdapter
from .adapters.java_adapter import JavaExecutionAdapter
from .diagnostics import Diagnostic, DiagnosticPhase, CompilationResult, ExecutionResult
from .pipeline import compile_source

__all__ = [
    "Token",
    "TokenType",
    "KEYWORDS",
    "C_KEYWORDS",
    "PYTHON_KEYWORDS",
    "JAVA_KEYWORDS",
    "Lexer",
    "CLexer",
    "PythonLexer",
    "JavaLexer",
    "Parser",
    "CParser",
    "PythonParser",
    "JavaParser",
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
    "StringLiteralNode",
    "VariableNode",
    "FunctionCallNode",
    "ReturnNode",
    "BlockNode",
    "IfNode",
    "WhileNode",
    "FunctionDefNode",
    "ClassDefNode",
    "PreprocessorNode",
    "GenericNode",
    "SemanticAnalyzer",
    "SymbolTable",
    "Symbol",
    "TACGenerator",
    "TACInstruction",
    "ToolchainManager",
    "toolchain_manager",
    "BaseExecutionAdapter",
    "CExecutionAdapter",
    "PythonExecutionAdapter",
    "JavaExecutionAdapter",
    "Diagnostic",
    "DiagnosticPhase",
    "CompilationResult",
    "ExecutionResult",
    "compile_source",
]
