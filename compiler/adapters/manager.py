"""
Compiler Execution Adapter Manager.
Coordinates toolchain detection, version checking, and execution dispatching for C, Python, and Java.
"""

from typing import Dict
from compiler.diagnostics import ExecutionResult
from .base_adapter import BaseExecutionAdapter
from .c_adapter import CExecutionAdapter
from .python_adapter import PythonExecutionAdapter
from .java_adapter import JavaExecutionAdapter


class ToolchainManager:
    """Manages language adapters and execution requests."""

    def __init__(self):
        self.adapters: Dict[str, BaseExecutionAdapter] = {
            "c": CExecutionAdapter(),
            "python": PythonExecutionAdapter(),
            "java": JavaExecutionAdapter(),
        }

    def get_adapter(self, language: str) -> BaseExecutionAdapter:
        lang_key = language.lower().strip()
        if lang_key in self.adapters:
            return self.adapters[lang_key]
        raise ValueError(f"Unsupported language '{language}'. Supported languages: 'c', 'python', 'java'.")

    def check_all_toolchains(self) -> Dict[str, Dict[str, str]]:
        return {lang: adapter.check_toolchain() for lang, adapter in self.adapters.items()}

    def execute(self, source_code: str, language: str = "c") -> ExecutionResult:
        adapter = self.get_adapter(language)
        return adapter.execute(source_code)


# Global default instance
toolchain_manager = ToolchainManager()

