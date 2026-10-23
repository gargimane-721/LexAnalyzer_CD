"""
Base execution adapter interface.
Defines execution contract and environment isolation.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict
from compiler.diagnostics import ExecutionResult


class BaseExecutionAdapter(ABC):
    """Abstract base class for compiling and running language code."""

    def __init__(self, timeout_sec: float = 5.0):
        self.timeout_sec = timeout_sec

    @abstractmethod
    def check_toolchain(self) -> Dict[str, str]:
        """Returns {'available': bool, 'name': str, 'version': str, 'guidance': str}."""
        pass

    @abstractmethod
    def execute(self, source_code: str) -> ExecutionResult:
        """Compiles and executes source code in an isolated subprocess."""
        pass

