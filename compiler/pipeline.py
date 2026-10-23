"""
Unified Compiler Pipeline with Multi-Language Support.
Coordinates Lexical, Syntax, Semantic, Intermediate Code Generation,
and Toolchain Execution for C, Python, and Java.
"""

import time
from typing import Optional, List, Any
from .tokens import Token
from .lexers.c_lexer import CLexer
from .lexers.python_lexer import PythonLexer
from .lexers.java_lexer import JavaLexer
from .parsers.c_parser import CParser
from .parsers.python_parser import PythonParser
from .parsers.java_parser import JavaParser
from .semantic import SemanticAnalyzer, SymbolTable, Symbol
from .tac import TACGenerator
from .adapters.manager import toolchain_manager
from .diagnostics import CompilationResult, Diagnostic, DiagnosticPhase, ExecutionResult


def compile_source(
    source_code: str,
    language: str = "c",
    stop_on_lexical_error: bool = False,
    execute: bool = False
) -> CompilationResult:
    """
    Executes the multi-language compiler pipeline on the provided source code.
    Routes to language-specific Lexer, Parser, and Compiler Adapter.
    """
    start_time = time.perf_counter()
    all_diagnostics: List[Diagnostic] = []
    lang_clean = language.lower().strip() if language else "c"

    # -------------------------------------------------------------
    # Phase 1: Language-Specific Lexical Analysis
    # -------------------------------------------------------------
    if lang_clean == "python":
        lexer = PythonLexer(source_code)
    elif lang_clean == "java":
        lexer = JavaLexer(source_code)
    else:
        lexer = CLexer(source_code)

    tokens, lex_diagnostics = lexer.tokenize()
    all_diagnostics.extend(lex_diagnostics)

    if stop_on_lexical_error and lex_diagnostics:
        elapsed = (time.perf_counter() - start_time) * 1000.0
        return CompilationResult(
            source_code=source_code,
            status="FAILED",
            language=lang_clean,
            tokens=tokens,
            ast=None,
            symbol_table=None,
            tac_instructions=[],
            diagnostics=all_diagnostics,
            duration_ms=round(elapsed, 2)
        )

    # -------------------------------------------------------------
    # Phase 2: Language-Specific Syntax Analysis
    # -------------------------------------------------------------
    if lang_clean == "python":
        parser = PythonParser(tokens, source_code=source_code)
    elif lang_clean == "java":
        parser = JavaParser(tokens, source_code=source_code)
    else:
        parser = CParser(tokens, source_code=source_code)

    ast, parse_diagnostics = parser.parse()
    all_diagnostics.extend(parse_diagnostics)

    has_fatal_syntax = any(d.phase == DiagnosticPhase.SYNTAX for d in parse_diagnostics)

    # -------------------------------------------------------------
    # Phase 3: Semantic Analysis / Symbol Table
    # -------------------------------------------------------------
    symbol_table = None
    if ast and not has_fatal_syntax:
        if lang_clean == "c":
            analyzer = SemanticAnalyzer()
            symbol_table, sem_diagnostics = analyzer.analyze(ast)
            all_diagnostics.extend(sem_diagnostics)
        else:
            # Build general symbol table for Python and Java
            symbol_table = SymbolTable()
            _extract_symbols(ast, symbol_table, lang_clean)

    # -------------------------------------------------------------
    # Phase 4: Intermediate Code Generation (Three-Address Code)
    # -------------------------------------------------------------
    tac_instructions: List[str] = []
    has_semantic_errors = any(
        d.phase == DiagnosticPhase.SEMANTIC and not d.error_code.endswith("5")
        for d in all_diagnostics
    )

    if ast and not has_fatal_syntax and not has_semantic_errors:
        tac_gen = TACGenerator()
        tac_instructions = tac_gen.generate(ast)

    # -------------------------------------------------------------
    # Phase 5: Optional Real Toolchain Execution
    # -------------------------------------------------------------
    exec_result: Optional[ExecutionResult] = None
    if execute and not has_fatal_syntax and not any(d.phase == DiagnosticPhase.LEXICAL for d in all_diagnostics):
        exec_result = toolchain_manager.execute(source_code, language=lang_clean)

    elapsed = (time.perf_counter() - start_time) * 1000.0

    has_errors = any(
        d.error_code not in ("SEM005",)
        for d in all_diagnostics
    )
    status = "FAILED" if has_errors else "SUCCESS"

    return CompilationResult(
        source_code=source_code,
        status=status,
        language=lang_clean,
        tokens=tokens,
        ast=ast,
        symbol_table=symbol_table,
        tac_instructions=tac_instructions,
        diagnostics=all_diagnostics,
        duration_ms=round(elapsed, 2),
        execution_result=exec_result
    )


def _extract_symbols(node: Any, sym_table: SymbolTable, language: str) -> None:
    """Extracts declared variables, functions, and classes into the symbol table."""
    if not node:
        return

    statements = getattr(node, "statements", None)
    if isinstance(statements, list):
        for stmt in statements:
            s_type = type(stmt).__name__
            line = getattr(stmt, "line", 1)
            col = getattr(stmt, "column", 1)

            if s_type == "DeclarationNode":
                sym_table.insert(Symbol(
                    name=stmt.identifier,
                    var_type=stmt.var_type,
                    line_declared=line,
                    column_declared=col,
                    is_initialized=True,
                    last_assigned_line=line
                ))
            elif s_type == "FunctionDefNode":
                sym_table.insert(Symbol(
                    name=f"{stmt.name}()",
                    var_type=f"function -> {stmt.return_type}",
                    line_declared=line,
                    column_declared=col,
                    is_initialized=True,
                    last_assigned_line=line
                ))
            elif s_type == "ClassDefNode":
                sym_table.insert(Symbol(
                    name=stmt.name,
                    var_type="class",
                    line_declared=line,
                    column_declared=col,
                    is_initialized=True,
                    last_assigned_line=line
                ))
            elif s_type == "GenericNode":
                if stmt.name == "Assignment":
                    target = stmt.details.get("target", "var")
                    sym_table.insert(Symbol(
                        name=target,
                        var_type="variable",
                        line_declared=line,
                        column_declared=col,
                        is_initialized=True,
                        last_assigned_line=line
                    ))
