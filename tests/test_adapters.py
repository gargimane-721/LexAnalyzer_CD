"""
Tests for compiler and execution adapters (C, Python, Java).
"""

import pytest
from compiler.adapters.manager import toolchain_manager
from compiler.pipeline import compile_source


def test_python_execution_output_30():
    source = """
x = 10
y = 20
print(x + y)
"""
    result = toolchain_manager.execute(source, language="python")
    assert result.success is True
    assert result.exit_code == 0
    assert result.stdout.strip() == "30"


def test_java_compilation_and_execution_30():
    source = """
public class Main {
    public static void main(String[] args) {
        int x = 10;
        int y = 20;
        System.out.println(x + y);
    }
}
"""
    result = toolchain_manager.execute(source, language="java")
    if result.toolchain_available:
        assert result.success is True
        assert result.exit_code == 0
        assert result.stdout.strip() == "30"
    else:
        # If JDK is not installed in the test environment, verify guidance is reported cleanly
        assert result.toolchain_available is False
        assert "guidance" in result.to_dict()


def test_c_adapter_toolchain_reporting():
    # C adapter should report status and guidance gracefully without raising exceptions
    adapter = toolchain_manager.get_adapter("c")
    info = adapter.check_toolchain()
    assert "available" in info
    assert "guidance" in info
    assert "name" in info


def test_pipeline_with_execution_flag():
    source = "print(15 + 15)"
    res = compile_source(source, language="python", execute=True)

    assert res.status == "SUCCESS"
    assert res.execution_result is not None
    assert res.execution_result.success is True
    assert res.execution_result.stdout.strip() == "30"


def test_language_switching_in_pipeline():
    # 1. Compile C
    c_res = compile_source("int a = 10; print(a);", language="c")
    assert c_res.status == "SUCCESS"
    assert c_res.language == "c"

    # 2. Compile Python
    py_res = compile_source("x = 10\nprint(x)", language="python")
    assert py_res.status == "SUCCESS"
    assert py_res.language == "python"

    # 3. Compile Java
    java_res = compile_source("public class Main { public static void main(String[] args) { int x = 10; } }", language="java")
    assert java_res.status == "SUCCESS"
    assert java_res.language == "java"

