"""
Python Language Execution Adapter.
Executes Python source code in an isolated subprocess with security timeouts.
"""

import os
import sys
import subprocess
import tempfile
import time
from typing import Dict
from compiler.diagnostics import ExecutionResult
from .base_adapter import BaseExecutionAdapter


class PythonExecutionAdapter(BaseExecutionAdapter):
    """Adapter for executing Python programs safely via subprocess."""

    def check_toolchain(self) -> Dict[str, str]:
        py_ver = f"Python {sys.version.split()[0]}"
        return {
            "available": True,
            "name": "Python Interpreter",
            "version": py_ver,
            "guidance": f"Running via configured interpreter: {sys.executable}"
        }

    def execute(self, source_code: str) -> ExecutionResult:
        tool_info = self.check_toolchain()
        start_time = time.perf_counter()

        with tempfile.TemporaryDirectory() as temp_dir:
            script_file = os.path.join(temp_dir, "script.py")

            with open(script_file, "w", encoding="utf-8") as f:
                f.write(source_code)

            # Restrict environment variables: do not propagate application secrets or DB
            env = os.environ.copy()
            env.pop("DATABASE_URL", None)
            env.pop("SECRET_KEY", None)
            env["PYTHONUNBUFFERED"] = "1"

            try:
                proc = subprocess.run(
                    [sys.executable, "-u", script_file],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    env=env,
                    timeout=self.timeout_sec
                )
                elapsed = (time.perf_counter() - start_time) * 1000.0

                is_success = (proc.returncode == 0)
                guidance = "Python execution finished successfully." if is_success else f"Process exited with error code {proc.returncode}."

                return ExecutionResult(
                    success=is_success,
                    toolchain_name=tool_info["name"],
                    toolchain_version=tool_info["version"],
                    toolchain_available=True,
                    exit_code=proc.returncode,
                    stdout=proc.stdout[:50000],
                    stderr=proc.stderr[:50000],
                    duration_ms=round(elapsed, 2),
                    guidance=guidance
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult(
                    success=False,
                    toolchain_name=tool_info["name"],
                    toolchain_version=tool_info["version"],
                    toolchain_available=True,
                    exit_code=-1,
                    stdout="",
                    stderr=f"Execution timed out after {self.timeout_sec} seconds. Check for infinite loops or input() calls.",
                    duration_ms=(time.perf_counter() - start_time) * 1000.0,
                    guidance="Ensure your code does not pause for interactive input or run infinite loops."
                )
            except Exception as e:
                return ExecutionResult(
                    success=False,
                    toolchain_name=tool_info["name"],
                    toolchain_version=tool_info["version"],
                    toolchain_available=True,
                    exit_code=-1,
                    stdout="",
                    stderr=f"Failed to execute Python process: {str(e)}",
                    duration_ms=(time.perf_counter() - start_time) * 1000.0
                )

