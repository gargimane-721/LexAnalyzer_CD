"""
Adapters package for real compilation and execution.
"""

from .base_adapter import BaseExecutionAdapter
from .c_adapter import CExecutionAdapter
from .python_adapter import PythonExecutionAdapter
from .java_adapter import JavaExecutionAdapter
from .manager import ToolchainManager, toolchain_manager

__all__ = [
    "BaseExecutionAdapter",
    "CExecutionAdapter",
    "PythonExecutionAdapter",
    "JavaExecutionAdapter",
    "ToolchainManager",
    "toolchain_manager",
]

