"""
Database Connection Manager for SQLite.
Ensures foreign-key enforcement, initializes schema, and provides connection context.
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import Generator

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "compiler.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


class DatabaseManager:
    """Manages SQLite database connections and schema lifecycle."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Creates a connection with foreign keys enabled and row factory set to sqlite3.Row."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def session(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager providing an active connection wrapped in a transaction."""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self) -> None:
        """Initializes tables and indexes from schema.sql and runs migrations."""
        if os.path.exists(SCHEMA_PATH):
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                schema_sql = f.read()

            conn = self.get_connection()
            try:
                conn.executescript(schema_sql)
                conn.commit()

                # Migration: Ensure 'language' column exists in programs and compilations
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(programs);")
                columns_programs = [row[1] for row in cursor.fetchall()]
                if "language" not in columns_programs and "programs" in [
                    r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                ]:
                    conn.execute("ALTER TABLE programs ADD COLUMN language TEXT NOT NULL DEFAULT 'c';")
                    conn.commit()

                cursor.execute("PRAGMA table_info(compilations);")
                columns_compilations = [row[1] for row in cursor.fetchall()]
                if "language" not in columns_compilations and "compilations" in [
                    r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                ]:
                    conn.execute("ALTER TABLE compilations ADD COLUMN language TEXT NOT NULL DEFAULT 'c';")
                    conn.commit()

            finally:
                conn.close()


# Global default instance
db_manager = DatabaseManager()
