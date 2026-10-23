-- Smart Lexical Analyzer & Syntax Checker SQLite Schema
-- Target Database: compiler.db

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    source_code TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'c',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS compilations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    program_id INTEGER NULL,
    program_name_snapshot TEXT,
    source_code_snapshot TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'c',
    status TEXT NOT NULL,
    token_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_ms REAL NOT NULL DEFAULT 0.0,
    FOREIGN KEY (program_id) REFERENCES programs(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    compilation_id INTEGER NOT NULL,
    token_type TEXT NOT NULL,
    lexeme TEXT NOT NULL,
    line INTEGER NOT NULL,
    column_number INTEGER NOT NULL,
    FOREIGN KEY (compilation_id) REFERENCES compilations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    compilation_id INTEGER NOT NULL,
    phase TEXT NOT NULL,
    error_code TEXT NOT NULL,
    message TEXT NOT NULL,
    line INTEGER NULL,
    column_number INTEGER NULL,
    FOREIGN KEY (compilation_id) REFERENCES compilations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS compilation_artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    compilation_id INTEGER NOT NULL,
    artifact_type TEXT NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (compilation_id) REFERENCES compilations(id) ON DELETE CASCADE
);

-- Indexes for fast querying of history and relations
CREATE INDEX IF NOT EXISTS idx_compilations_program_id ON compilations(program_id);
CREATE INDEX IF NOT EXISTS idx_compilations_started_at ON compilations(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_tokens_compilation_id ON tokens(compilation_id);
CREATE INDEX IF NOT EXISTS idx_errors_compilation_id ON errors(compilation_id);
