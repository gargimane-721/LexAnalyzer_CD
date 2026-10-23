"""
Java Language Compilation and Execution Adapter.
Compiles Java source code using javac and runs bytecode via java.
Handles public class name extraction and student statement wrapping.
"""

import os
import re
import shutil
import subprocess
import tempfile
import time
from typing import Dict, Optional, Tuple
from compiler.diagnostics import ExecutionResult
from .base_adapter import BaseExecutionAdapter


class JavaExecutionAdapter(BaseExecutionAdapter):
    """Adapter for compiling and executing Java programs via javac and java."""

    JAVA_SEARCH_PATHS = [
        r"C:\Program Files\Eclipse Adoptium\jdk-25.0.3.9-hotspot\bin",
        r"C:\Program Files\Java\jdk-21\bin",
        r"C:\Program Files\Java\jdk-17\bin",
        r"C:\Program Files\Java\jdk-11\bin",
    ]

    def find_java_tools(self) -> Tuple[Optional[str], Optional[str]]:
        javac = shutil.which("javac")
        java = shutil.which("java")

        if javac and java:
            return javac, java

        # Search known paths on Windows
        for sp in self.JAVA_SEARCH_PATHS:
            test_javac = os.path.join(sp, "javac.exe")
            test_java = os.path.join(sp, "java.exe")
            if os.path.exists(test_javac) and os.path.exists(test_java):
                return test_javac, test_java

        return javac, java

    def check_toolchain(self) -> Dict[str, str]:
        javac, java = self.find_java_tools()
        if not javac or not java:
            return {
                "available": False,
                "name": "Java Development Kit (JDK)",
                "version": "Not installed",
                "guidance": (
                    "Java compiler (javac) or runtime (java) was not found in PATH.\n"
                    "To enable real Java compilation and execution:\n"
                    "1. Install OpenJDK (Eclipse Adoptium Temurin): winget install EclipseAdoptium.Temurin.21.JDK\n"
                    "2. Ensure the JDK /bin folder is added to your PATH environment variable."
                )
            }

        try:
            res = subprocess.run([javac, "-version"], capture_output=True, text=True, timeout=3.0)
            ver = res.stdout.strip() or res.stderr.strip() or "Java JDK"
            return {
                "available": True,
                "name": "Java Development Kit",
                "version": ver,
                "guidance": f"JDK active: {javac}"
            }
        except Exception as e:
            return {
                "available": True,
                "name": "Java JDK",
                "version": "Detected",
                "guidance": f"Found at {javac} ({e})"
            }

    def extract_class_name(self, source_code: str) -> Tuple[str, str]:
        """
        Extracts the class name or wraps bare statements into a Main class.
        Returns (class_name, final_source_code).
        """
        # Look for public class First, then any class
        pub_match = re.search(r"public\s+class\s+([A-Za-z0-9_$]+)", source_code)
        if pub_match:
            return pub_match.group(1), source_code

        class_match = re.search(r"class\s+([A-Za-z0-9_$]+)", source_code)
        if class_match:
            return class_match.group(1), source_code

        # If no class keyword is found, wrap bare statements in a Main wrapper for student convenience
        wrapped = (
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            f"        {source_code.strip()}\n"
            "    }\n"
            "}\n"
        )
        return "Main", wrapped

    def execute(self, source_code: str) -> ExecutionResult:
        tool_info = self.check_toolchain()
        javac, java = self.find_java_tools()

        if not javac or not java:
            return ExecutionResult(
                success=False,
                toolchain_name="Java Development Kit (JDK)",
                toolchain_version="Not Available",
                toolchain_available=False,
                exit_code=-1,
                stdout="",
                stderr="Java JDK compiler (javac) is not available on this system.",
                duration_ms=0.0,
                guidance=tool_info["guidance"]
            )

        start_time = time.perf_counter()
        class_name, final_code = self.extract_class_name(source_code)

        with tempfile.TemporaryDirectory() as temp_dir:
            java_file = os.path.join(temp_dir, f"{class_name}.java")

            with open(java_file, "w", encoding="utf-8") as f:
                f.write(final_code)

            # 1. Compile Phase (javac)
            try:
                compile_res = subprocess.run(
                    [javac, f"{class_name}.java"],
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
                    stderr=f"javac compilation timed out after {self.timeout_sec} seconds.",
                    duration_ms=(time.perf_counter() - start_time) * 1000.0,
                    guidance="Check for complex nested definitions or classpath issues."
                )
            except Exception as e:
                return ExecutionResult(
                    success=False,
                    toolchain_name=tool_info["name"],
                    toolchain_version=tool_info["version"],
                    toolchain_available=True,
                    exit_code=-1,
                    stdout="",
                    stderr=f"Failed to execute javac: {str(e)}",
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
                    guidance="Review Java compiler diagnostics above. Ensure class names match filenames and semicolons are present."
                )

            # 2. Execution Phase (java)
            try:
                run_res = subprocess.run(
                    [java, "-cp", ".", class_name],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    timeout=self.timeout_sec
                )
                elapsed = (time.perf_counter() - start_time) * 1000.0
                is_success = (run_res.returncode == 0)

                return ExecutionResult(
                    success=is_success,
                    toolchain_name=tool_info["name"],
                    toolchain_version=tool_info["version"],
                    toolchain_available=True,
                    exit_code=run_res.returncode,
                    stdout=run_res.stdout[:50000],
                    stderr=run_res.stderr[:50000],
                    duration_ms=round(elapsed, 2),
                    guidance="Java program executed successfully." if is_success else f"Process exited with code {run_res.returncode}."
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult(
                    success=False,
                    toolchain_name=tool_info["name"],
                    toolchain_version=tool_info["version"],
                    toolchain_available=True,
                    exit_code=-1,
                    stdout="",
                    stderr=f"Execution timed out after {self.timeout_sec} seconds. Check for infinite loops or scanner/input prompts.",
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
                    stderr=f"Runtime error executing Java program: {str(e)}",
                    duration_ms=(time.perf_counter() - start_time) * 1000.0
                )

