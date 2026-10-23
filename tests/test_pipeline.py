"""
Integration tests for the unified compiler pipeline.
"""

import pytest
from compiler.pipeline import compile_source


def test_pipeline_valid_program():
    source = """
    int a = 10;
    float b = 2.5;
    int c = a + 5;
    print(c);
    """
    res = compile_source(source)

    assert res.status == "SUCCESS"
    assert res.is_success is True
    assert res.token_count > 0
    assert res.error_count == 0
    assert res.ast is not None
    assert res.symbol_table is not None
    assert len(res.tac_instructions) > 0
    assert res.duration_ms >= 0.0


def test_pipeline_lexical_failure():
    source = "int a = 10 @ 20;"
    res = compile_source(source)

    assert res.status == "FAILED"
    assert res.error_count > 0
    assert any(d.phase.value == "LEXICAL" for d in res.diagnostics)


def test_pipeline_syntax_failure():
    source = "int a = 10 \n int b = 20;"
    res = compile_source(source)

    assert res.status == "FAILED"
    assert res.error_count > 0
    assert any(d.phase.value == "SYNTAX" for d in res.diagnostics)


def test_pipeline_semantic_failure():
    source = "int a = 10; print(undefinedVar);"
    res = compile_source(source)

    assert res.status == "FAILED"
    assert any(d.phase.value == "SEMANTIC" for d in res.diagnostics)

