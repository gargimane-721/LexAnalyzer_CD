"""
Repository Access Layer for Programs, Compilations, Tokens, and Diagnostics.
Provides clean parameterized queries, transactions, and reporting methods.
"""

import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from .db import DatabaseManager, db_manager
from compiler.diagnostics import CompilationResult, DiagnosticPhase


class CompilerRepository:
    """Handles persistence and retrieval for all compiler database entities."""

    def __init__(self, manager: Optional[DatabaseManager] = None):
        self.manager = manager or db_manager

    # -------------------------------------------------------------
    # Programs CRUD
    # -------------------------------------------------------------

    def create_program(self, name: str, source_code: str, language: str = "c") -> int:
        """Saves a new source program into the database."""
        now = datetime.now().isoformat()
        with self.manager.session() as conn:
            cursor = conn.execute(
                """
                INSERT INTO programs (name, source_code, language, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name.strip(), source_code, language.lower().strip(), now, now)
            )
            return cursor.lastrowid

    def get_program(self, program_id: int) -> Optional[Dict[str, Any]]:
        """Fetches a saved program by its ID."""
        with self.manager.session() as conn:
            row = conn.execute(
                "SELECT * FROM programs WHERE id = ?",
                (program_id,)
            ).fetchone()
            return dict(row) if row else None

    def list_programs(self, search_query: Optional[str] = None, language_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists all saved programs, optionally filtered by keyword and language."""
        with self.manager.session() as conn:
            query = "SELECT id, name, source_code, language, created_at, updated_at FROM programs WHERE 1=1"
            params: list = []

            if language_filter and language_filter.lower() != "all":
                query += " AND language = ?"
                params.append(language_filter.lower().strip())

            if search_query:
                query += " AND (name LIKE ? OR source_code LIKE ?)"
                pattern = f"%{search_query.strip()}%"
                params.extend([pattern, pattern])

            query += " ORDER BY updated_at DESC"
            rows = conn.execute(query, tuple(params)).fetchall()
            return [dict(r) for r in rows]

    def update_program(
        self,
        program_id: int,
        name: Optional[str] = None,
        source_code: Optional[str] = None,
        language: Optional[str] = None
    ) -> bool:
        """Updates the name, source code, and/or language of an existing program."""
        now = datetime.now().isoformat()
        with self.manager.session() as conn:
            existing = conn.execute("SELECT * FROM programs WHERE id = ?", (program_id,)).fetchone()
            if not existing:
                return False

            existing_dict = dict(existing)
            new_name = name.strip() if name is not None else existing_dict["name"]
            new_source = source_code if source_code is not None else existing_dict["source_code"]
            new_lang = language.lower().strip() if language is not None else existing_dict.get("language", "c")

            cursor = conn.execute(
                """
                UPDATE programs
                SET name = ?, source_code = ?, language = ?, updated_at = ?
                WHERE id = ?
                """,
                (new_name, new_source, new_lang, now, program_id)
            )
            return cursor.rowcount > 0

    def delete_program(self, program_id: int) -> bool:
        """Deletes a program. Note: Foreign keys will preserve compilations by setting program_id = NULL."""
        with self.manager.session() as conn:
            cursor = conn.execute("DELETE FROM programs WHERE id = ?", (program_id,))
            return cursor.rowcount > 0

    # -------------------------------------------------------------
    # Compilation History & Artifact Recording
    # -------------------------------------------------------------

    def record_compilation(
        self,
        result: CompilationResult,
        program_id: Optional[int] = None,
        program_name: Optional[str] = None,
        language: str = "c"
    ) -> int:
        """
        Records a complete compilation pass atomically:
        - Header in `compilations`
        - Tokens in `tokens`
        - Errors in `errors`
        - AST and TAC in `compilation_artifacts`
        """
        now = datetime.now().isoformat()
        effective_name = program_name.strip() if program_name else "Untitled Script"
        effective_lang = getattr(result, "language", language) or language

        with self.manager.session() as conn:
            # 1. Insert header
            cursor = conn.execute(
                """
                INSERT INTO compilations (
                    program_id, program_name_snapshot, source_code_snapshot, language,
                    status, token_count, error_count, started_at, completed_at, duration_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    program_id,
                    effective_name,
                    result.source_code,
                    effective_lang.lower().strip(),
                    result.status,
                    result.token_count,
                    result.error_count,
                    now,
                    now,
                    result.duration_ms
                )
            )
            compilation_id = cursor.lastrowid

            # 2. Insert Tokens (excluding EOF)
            token_rows = [
                (
                    compilation_id,
                    t.token_type.value if hasattr(t.token_type, "value") else str(t.token_type),
                    t.lexeme,
                    t.line,
                    t.column
                )
                for t in result.tokens
                if getattr(t.token_type, "value", str(t.token_type)) != "EOF"
            ]
            if token_rows:
                conn.executemany(
                    """
                    INSERT INTO tokens (compilation_id, token_type, lexeme, line, column_number)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    token_rows
                )

            # 3. Insert Errors / Diagnostics
            diag_rows = [
                (
                    compilation_id,
                    d.phase.value if hasattr(d.phase, "value") else str(d.phase),
                    d.error_code,
                    d.message,
                    d.line,
                    d.column
                )
                for d in result.diagnostics
            ]
            if diag_rows:
                conn.executemany(
                    """
                    INSERT INTO errors (compilation_id, phase, error_code, message, line, column_number)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    diag_rows
                )

            # 4. Insert Artifacts (AST, TAC, Symbol Table)
            artifacts = []
            if result.ast:
                try:
                    ast_dict = result.ast.to_dict() if hasattr(result.ast, "to_dict") else {"ast": str(result.ast)}
                    artifacts.append((compilation_id, "AST", json.dumps(ast_dict)))
                except Exception:
                    artifacts.append((compilation_id, "AST", str(result.ast)))

            if result.symbol_table:
                try:
                    sym_data = result.symbol_table.to_list() if hasattr(result.symbol_table, "to_list") else str(result.symbol_table)
                    artifacts.append((compilation_id, "SYMBOL_TABLE", json.dumps(sym_data)))
                except Exception:
                    pass

            if result.tac_instructions:
                artifacts.append((compilation_id, "TAC", "\n".join(result.tac_instructions)))

            if artifacts:
                conn.executemany(
                    """
                    INSERT INTO compilation_artifacts (compilation_id, artifact_type, content)
                    VALUES (?, ?, ?)
                    """,
                    artifacts
                )

            return compilation_id

    def get_recent_compilations(
        self,
        limit: int = 50,
        status_filter: Optional[str] = None,
        language_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieves list of compilation records ordered from newest to oldest."""
        with self.manager.session() as conn:
            query = """
                SELECT id, program_id, program_name_snapshot, language, status,
                       token_count, error_count, started_at, duration_ms
                FROM compilations
                WHERE 1=1
            """
            params: list = []

            if status_filter and status_filter.upper() in ("SUCCESS", "FAILED"):
                query += " AND status = ?"
                params.append(status_filter.upper())

            if language_filter and language_filter.lower() != "all":
                query += " AND language = ?"
                params.append(language_filter.lower().strip())

            query += " ORDER BY started_at DESC, id DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, tuple(params)).fetchall()
            return [dict(r) for r in rows]

    def get_compilation_details(self, compilation_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves comprehensive information for a past compilation run."""
        with self.manager.session() as conn:
            comp_row = conn.execute(
                "SELECT * FROM compilations WHERE id = ?",
                (compilation_id,)
            ).fetchone()

            if not comp_row:
                return None

            details = dict(comp_row)

            # Fetch tokens
            tok_rows = conn.execute(
                "SELECT token_type, lexeme, line, column_number FROM tokens WHERE compilation_id = ? ORDER BY id ASC",
                (compilation_id,)
            ).fetchall()
            details["tokens"] = [dict(r) for r in tok_rows]

            # Fetch errors
            err_rows = conn.execute(
                "SELECT phase, error_code, message, line, column_number FROM errors WHERE compilation_id = ? ORDER BY id ASC",
                (compilation_id,)
            ).fetchall()
            details["errors"] = [dict(r) for r in err_rows]

            # Fetch artifacts
            art_rows = conn.execute(
                "SELECT artifact_type, content FROM compilation_artifacts WHERE compilation_id = ?",
                (compilation_id,)
            ).fetchall()
            details["artifacts"] = {r["artifact_type"]: r["content"] for r in art_rows}

            return details

    # -------------------------------------------------------------
    # Dashboard Aggregates
    # -------------------------------------------------------------

    def get_dashboard_statistics(self) -> Dict[str, Any]:
        """Calculates live metrics from the SQLite database."""
        with self.manager.session() as conn:
            total_progs = conn.execute("SELECT COUNT(*) FROM programs").fetchone()[0]
            total_comps = conn.execute("SELECT COUNT(*) FROM compilations").fetchone()[0]
            success_comps = conn.execute("SELECT COUNT(*) FROM compilations WHERE status = 'SUCCESS'").fetchone()[0]
            failed_comps = conn.execute("SELECT COUNT(*) FROM compilations WHERE status = 'FAILED'").fetchone()[0]

            rate = round((success_comps / total_comps * 100.0), 1) if total_comps > 0 else 0.0

            # Language breakdown
            lang_counts = {}
            try:
                lang_rows = conn.execute("SELECT language, COUNT(*) FROM compilations GROUP BY language").fetchall()
                lang_counts = {r[0]: r[1] for r in lang_rows}
            except Exception:
                pass

            return {
                "total_programs": total_progs,
                "total_compilations": total_comps,
                "successful_compilations": success_comps,
                "failed_compilations": failed_comps,
                "success_rate": rate,
                "language_breakdown": lang_counts,
            }
