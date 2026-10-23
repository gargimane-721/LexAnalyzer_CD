"""
Diagnostic and error reporting module for the compiler.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional


class DiagnosticPhase(str, Enum):
    LEXICAL = "LEXICAL"
    SYNTAX = "SYNTAX"
    SEMANTIC = "SEMANTIC"
    DATABASE = "DATABASE"


@dataclass
class Diagnostic:
    """Represents a compiler error or warning with contextual diagnostics."""
    phase: DiagnosticPhase
    error_code: str
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    suggestion: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "phase": self.phase.value,
            "error_code": self.error_code,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "suggestion": self.suggestion,
        }

    def __str__(self) -> str:
        loc = f" at line {self.line}, column {self.column}" if self.line is not None else ""
        return f"[{self.phase.value} ERROR {self.error_code}]{loc}: {self.message}"


@dataclass
class CompilationResult:
    """Encapsulates all results and artifacts from a complete compilation pass."""
    source_code: str
    status: str  # "SUCCESS" or "FAILED"
    tokens: List[Any] = field(default_factory=list)
    ast: Optional[Any] = None
    symbol_table: Optional[Any] = None
    tac_instructions: List[str] = field(default_factory=list)
    diagnostics: List[Diagnostic] = field(default_factory=list)
    duration_ms: float = 0.0

    @property
    def token_count(self) -> int:
        # Exclude EOF from count for user-facing metrics
        return len([t for t in self.tokens if getattr(t, "token_type", None) != "EOF" and getattr(t.token_type, "value", "") != "EOF"])

    @property
    def error_count(self) -> int:
        return len(self.diagnostics)

    @property
    def is_success(self) -> bool:
        return self.status == "SUCCESS" and len(self.diagnostics) == 0

