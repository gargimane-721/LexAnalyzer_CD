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
        """Initializes tables and indexes from schema.sql if not already present."""
        if os.path.exists(SCHEMA_PATH):
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                schema_sql = f.read()

            conn = self.get_connection()
            try:
                conn.executescript(schema_sql)
                conn.commit()
            finally:
                conn.close()


# Global default instance
db_manager = DatabaseManager()

