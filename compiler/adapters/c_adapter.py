"""
C Language Compilation and Execution Adapter.
Compiles C code using GCC or Clang and runs the resulting binary in an isolated subprocess.
"""

import os
import shutil
import subprocess
import tempfile
import time
from typing import Dict, Optional
from compiler.diagnostics import ExecutionResult
from .base_adapter import BaseExecutionAdapter


class CExecutionAdapter(BaseExecutionAdapter):
    """Adapter for compiling and executing C code via GCC or Clang."""

    C_CANDIDATE_PATHS = [
        r"C:\msys64\mingw64\bin\gcc.exe",
        r"C:\msys64\ucrt64\bin\gcc.exe",
        r"C:\MinGW\bin\gcc.exe",
        r"C:\w64devkit\bin\gcc.exe",
        r"C:\Program Files\LLVM\bin\clang.exe",
    ]

    def find_c_compiler(self) -> Optional[str]:
        # 1. Search PATH
        cmd = shutil.which("gcc") or shutil.which("clang")
        if cmd:
            return cmd

        # 2. Search common Windows locations
        for p in self.C_CANDIDATE_PATHS:
            if os.path.exists(p):
                return p

        return None

    def check_toolchain(self) -> Dict[str, str]:
        cmd = self.find_c_compiler()
        if not cmd:
            return {
                "available": False,
                "name": "GCC / Clang",
                "version": "Not installed",
                "guidance": (
                    "C compiler (GCC or Clang) was not found in PATH.\n"
                    "To enable real C compilation on Windows:\n"
                    "1. Install MinGW-w64 via PowerShell: winget install -e --id GnuWin32.GCC\n"
                    "   OR install MSYS2: winget install MSYS2.MSYS2\n"
                    "2. Or download w64devkit from GitHub and add its /bin folder to PATH."
                )
            }

        try:
            res = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=3.0)
            first_line = res.stdout.splitlines()[0] if res.stdout else "GCC / Clang"
            return {
                "available": True,
                "name": os.path.basename(cmd),
                "version": first_line,
                "guidance": f"Compiler active: {cmd}"
            }
        except Exception as e:
            return {
                "available": True,
                "name": os.path.basename(cmd),
                "version": "Detected",
                "guidance": f"Found at {cmd} (status: {e})"
            }

    def execute(self, source_code: str) -> ExecutionResult:
        tool_info = self.check_toolchain()
        cmd = self.find_c_compiler()

        if not cmd:
            return ExecutionResult(
                success=False,
                toolchain_name="GCC / Clang",
                toolchain_version="Not Available",
                toolchain_available=False,
                exit_code=-1,
                stdout="",
                stderr="C compiler toolchain (GCC or Clang) is not installed on this system.",
                duration_ms=0.0,
                guidance=tool_info["guidance"]
            )

        start_time = time.perf_counter()

        with tempfile.TemporaryDirectory() as temp_dir:
            c_file = os.path.join(temp_dir, "program.c")
            exe_file = os.path.join(temp_dir, "program.exe")

            with open(c_file, "w", encoding="utf-8") as f:
                f.write(source_code)

            # 1. Compile Phase
            try:
                compile_res = subprocess.run(
                    [cmd, "-O2", c_file, "-o", exe_file],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    timeout=self.timeout_sec
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult(
                    success=False,
                    toolchain_name=tool_info["name"],
                    toolchain_version=tool_info["version"],
                    toolchain_available=True,
                    exit_code=-1,
                    stdout="",
                    stderr=f"Compilation timed out after {self.timeout_sec} seconds.",
                    duration_ms=(time.perf_counter() - start_time) * 1000.0,
                    guidance="Check for circular macros or excessively complex header inclusions."
                )
            except Exception as e:
                return ExecutionResult(
                    success=False,
                    toolchain_name=tool_info["name"],
                    toolchain_version=tool_info["version"],
                    toolchain_available=True,
                    exit_code=-1,
                    stdout="",
                    stderr=f"Failed to invoke compiler process: {str(e)}",
                    duration_ms=(time.perf_counter() - start_time) * 1000.0
                )

            if compile_res.returncode != 0:
                return ExecutionResult(
                    success=False,
                    toolchain_name=tool_info["name"],
                    toolchain_version=tool_info["version"],
                    toolchain_available=True,
                    exit_code=compile_res.returncode,
                    stdout=compile_res.stdout,
                    stderr=compile_res.stderr,
                    duration_ms=(time.perf_counter() - start_time) * 1000.0,
                    guidance="Review C compiler error messages above to correct syntax, types, or missing headers."
                )

            # 2. Execution Phase
            try:
                run_res = subprocess.run(
                    [exe_file],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    timeout=self.timeout_sec
                )
                elapsed = (time.perf_counter() - start_time) * 1000.0
                return ExecutionResult(
                    success=(run_res.returncode == 0),
                    toolchain_name=tool_info["name"],
                    toolchain_version=tool_info["version"],
                    toolchain_available=True,
                    exit_code=run_res.returncode,
                    stdout=run_res.stdout[:50000],  # capped at 50KB
                    stderr=run_res.stderr[:50000],
                    duration_ms=round(elapsed, 2),
                    guidance="Program executed successfully." if run_res.returncode == 0 else f"Process exited with non-zero status ({run_res.returncode})."
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult(
                    success=False,
                    toolchain_name=tool_info["name"],
                    toolchain_version=tool_info["version"],
                    toolchain_available=True,
                    exit_code=-1,
                    stdout="",
                    stderr=f"Execution timed out after {self.timeout_sec} seconds. Possible infinite loop.",
                    duration_ms=(time.perf_counter() - start_time) * 1000.0,
                    guidance="Ensure loops terminate properly."
                )
            except Exception as e:
                return ExecutionResult(
                    success=False,
                    toolchain_name=tool_info["name"],
                    toolchain_version=tool_info["version"],
                    toolchain_available=True,
                    exit_code=-1,
                    stdout="",
                    stderr=f"Runtime error executing binary: {str(e)}",
                    duration_ms=(time.perf_counter() - start_time) * 1000.0
                )

