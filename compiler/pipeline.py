"""
Unified Compiler Pipeline.
Coordinates Lexical, Syntax, Semantic, and Intermediate Code Generation phases.
"""

import time
from typing import Optional
from .tokens import Token
from .lexer import Lexer
from .parser import Parser
from .semantic import SemanticAnalyzer
from .tac import TACGenerator
from .diagnostics import CompilationResult, Diagnostic, DiagnosticPhase


def compile_source(source_code: str, stop_on_lexical_error: bool = False) -> CompilationResult:
    """
    Executes the full compiler pipeline on the provided source code.
    Returns a complete CompilationResult object containing all artifacts and diagnostics.
    """
    start_time = time.perf_counter()
    all_diagnostics: list[Diagnostic] = []

    # -------------------------------------------------------------
    # Phase 1: Lexical Analysis
    # -------------------------------------------------------------
    lexer = Lexer(source_code)
    tokens, lex_diagnostics = lexer.tokenize()
    all_diagnostics.extend(lex_diagnostics)

    if stop_on_lexical_error and lex_diagnostics:
        elapsed = (time.perf_counter() - start_time) * 1000.0
        return CompilationResult(
            source_code=source_code,
            status="FAILED",
            tokens=tokens,
            ast=None,
            symbol_table=None,
            tac_instructions=[],
            diagnostics=all_diagnostics,
            duration_ms=round(elapsed, 2)
        )

    # -------------------------------------------------------------
    # Phase 2: Syntax Analysis
    # -------------------------------------------------------------
    parser = Parser(tokens)
    ast, parse_diagnostics = parser.parse()
    all_diagnostics.extend(parse_diagnostics)

    # Check for fatal syntax errors
    has_fatal_syntax = any(d.phase == DiagnosticPhase.SYNTAX for d in parse_diagnostics)

    # -------------------------------------------------------------
    # Phase 3: Semantic Analysis (Run if AST is structurally available)
    # -------------------------------------------------------------
    symbol_table = None
    if ast and not has_fatal_syntax:
        analyzer = SemanticAnalyzer()
        symbol_table, sem_diagnostics = analyzer.analyze(ast)
        all_diagnostics.extend(sem_diagnostics)

    # -------------------------------------------------------------
    # Phase 4: Intermediate Code Generation (Run if no syntax or fatal semantic errors)
    # -------------------------------------------------------------
    tac_instructions: list[str] = []
    has_semantic_errors = any(
        d.phase == DiagnosticPhase.SEMANTIC and not d.error_code.endswith("5") # Exclude warnings
        for d in all_diagnostics
    )

    if ast and not has_fatal_syntax and not has_semantic_errors:
        tac_gen = TACGenerator()
        tac_instructions = tac_gen.generate(ast)

    elapsed = (time.perf_counter() - start_time) * 1000.0

    # Determine status
    has_errors = any(
        d.error_code not in ("SEM005",) # Warnings do not fail compilation
        for d in all_diagnostics
    )
    status = "FAILED" if has_errors else "SUCCESS"

    return CompilationResult(
        source_code=source_code,
        status=status,
        tokens=tokens,
        ast=ast,
        symbol_table=symbol_table,
        tac_instructions=tac_instructions,
        diagnostics=all_diagnostics,
        duration_ms=round(elapsed, 2)
    )

