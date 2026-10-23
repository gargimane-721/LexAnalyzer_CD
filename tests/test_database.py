"""
Unit tests for the SQLite Database layer and Repository.
"""

import os
import tempfile
import sqlite3
import pytest
from database.db import DatabaseManager
from database.repository import CompilerRepository
from compiler.pipeline import compile_source


@pytest.fixture
def repo():
    """Provides a fresh temporary SQLite database repository for each test."""
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, "test_compiler.db")
    mgr = DatabaseManager(temp_db_path)
    repository = CompilerRepository(mgr)
    yield repository
    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)


def test_program_crud_operations(repo):
    # 1. Create
    prog_id = repo.create_program("Test Prog", "int a = 10;")
    assert prog_id > 0

    # 2. Read
    prog = repo.get_program(prog_id)
    assert prog is not None
    assert prog["name"] == "Test Prog"
    assert prog["source_code"] == "int a = 10;"

    # 3. Update code and name
    updated = repo.update_program(prog_id, name="Updated Prog", source_code="int a = 20;")
    assert updated is True
    refreshed = repo.get_program(prog_id)
    assert refreshed["name"] == "Updated Prog"
    assert refreshed["source_code"] == "int a = 20;"

    # 4. List / Search
    results = repo.list_programs(search_query="Updated")
    assert len(results) == 1
    assert results[0]["id"] == prog_id

    # 5. Delete
    deleted = repo.delete_program(prog_id)
    assert deleted is True
    assert repo.get_program(prog_id) is None


def test_record_successful_compilation(repo):
    prog_id = repo.create_program("MathScript", "int a = 5; int b = a * 2; print(b);")
    res = compile_source("int a = 5; int b = a * 2; print(b);")

    comp_id = repo.record_compilation(res, program_id=prog_id, program_name="MathScript")
    assert comp_id > 0

    details = repo.get_compilation_details(comp_id)
    assert details is not None
    assert details["status"] == "SUCCESS"
    assert details["token_count"] == res.token_count
    assert details["error_count"] == 0
    assert len(details["tokens"]) == res.token_count
    assert "TAC" in details["artifacts"]
    assert "AST" in details["artifacts"]


def test_record_failed_compilation(repo):
    source = "int a = 10\nint b = 20;"  # Missing semicolon
    res = compile_source(source)

    comp_id = repo.record_compilation(res, program_name="BrokenScript")
    assert comp_id > 0

    details = repo.get_compilation_details(comp_id)
    assert details is not None
    assert details["status"] == "FAILED"
    assert details["error_count"] > 0
    assert len(details["errors"]) == details["error_count"]
    assert any(err["error_code"] == "SYN001" for err in details["errors"])


def test_foreign_key_enforcement(repo):
    # Foreign keys must prevent inserting orphaned tokens referencing non-existent compilations
    with pytest.raises(sqlite3.IntegrityError):
        with repo.manager.session() as conn:
            conn.execute(
                """
                INSERT INTO tokens (compilation_id, token_type, lexeme, line, column_number)
                VALUES (99999, 'IDENTIFIER', 'ghost', 1, 1)
                """
            )


def test_dashboard_statistics(repo):
    repo.create_program("P1", "int x = 1;")
    repo.create_program("P2", "int y = 2;")

    res_good = compile_source("int x = 1;")
    res_bad = compile_source("int x = @;")

    repo.record_compilation(res_good, program_name="Good")
    repo.record_compilation(res_bad, program_name="Bad")

    stats = repo.get_dashboard_statistics()
    assert stats["total_programs"] == 2
    assert stats["total_compilations"] == 2
    assert stats["successful_compilations"] == 1
    assert stats["failed_compilations"] == 1
    assert stats["success_rate"] == 50.0

