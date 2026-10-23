# System Architecture & Design Specification

## 1. Architectural Overview

The **Smart Lexical Analyzer & Syntax Checker** is built on a modular pipeline architecture adhering to the classic principles of compiler engineering. The platform separates compiler analysis passes from GUI presentation and database persistence layers.

```mermaid
flowchart TD
    Src["Source Code (C-like Input)"] --> Lexer["1. Lexical Analyzer (Scanner)"]
    Lexer -->|Token Stream + Coordinates| Parser["2. Syntax Analyzer (Parser)"]
    Lexer -->|Lexical Errors| Diag["Centralized Diagnostics"]
    Parser -->|Abstract Syntax Tree (AST)| Semantic["3. Semantic Analyzer & Symbol Table"]
    Parser -->|Syntax Errors| Diag
    Semantic -->|Decorated AST + Symbol Table| TAC["4. Intermediate Code Generator (TAC)"]
    Semantic -->|Semantic Errors| Diag
    TAC -->|Three-Address Code Instructions| Out["Compilation Result"]
    Diag --> Out
    Out --> Repo["SQLite Repository Layer (compiler.db)"]
    Out --> UI["Streamlit Interactive GUI"]
```

---

## 2. Core Compiler Pipeline Components

### 2.1 Lexical Analyzer (`compiler/lexer.py`)
- **Engine:** Python's compiled regular expression engine (`re`).
- **Tracking:** Maintains 1-based line and 1-based column offsets for precise diagnostic reporting.
- **Filtering:** Silently discards single-line comments (`//...`) and whitespace, while updating the line/column tracker accurately.
- **Resilience:** Unknown characters (e.g. `@`, `$`, `#`) or malformed floating literals (`12.34.56`) emit structured `Diagnostic` objects without aborting the scanner, allowing the tokenizer to recover and complete stream classification.

### 2.2 Syntax Analyzer (`compiler/parser.py`)
- **Paradigm:** Hand-crafted Top-Down Recursive-Descent Parser with $k=1$ token lookahead (`LL(1)` subset).
- **Precedence Hierarchy:**
  - `parse_expression()`: Handles additive operators (`+`, `-`)
  - `parse_term()`: Handles multiplicative operators (`*`, `/`)
  - `parse_factor()`: Handles literals, variables, parentheses `(...)`, and unary operators (`+`, `-`)
- **Error Synchronization:** If a syntax error is encountered (such as a missing semicolon or unexpected token), the parser reports the error and invokes `synchronize()` to discard tokens until the next statement delimiter (`;`, `int`, `float`, `print`, or `EOF`), enabling multi-error detection.

### 2.3 Semantic Analyzer (`compiler/semantic.py`)
- **Symbol Table:** An in-memory dictionary registering declared variables, declared types (`int`, `float`), source line coordinates, and initialization state.
- **Rule Verification:**
  - `SEM001`: Duplicate variable declaration in the same scope.
  - `SEM002`: Use of undeclared variable in assignments or expressions.
  - `SEM003`: Use of uninitialized variable.
  - `SEM004`: Static compile-time division by zero (e.g., `x / 0`).
  - `SEM005`: Type conversion warning (assigning `float` expression to `int` variable).

### 2.4 Intermediate Code Generator (`compiler/tac.py`)
- **Representation:** Linearized Three-Address Code (3AC/TAC).
- **Format:** Each instruction possesses at most one operator and at most three addresses (e.g. `t1 = b * 2`, `t2 = a + t1`, `c = t2`).
- **Safety:** Emitted only when preceding lexical, syntactic, and fatal semantic phases pass cleanly.

---

## 3. Database Layer (`database/`)

The persistence subsystem uses Python's built-in `sqlite3` driver with foreign key constraints enabled on all active connections:

- `database/schema.sql`: Declarative table and index definitions.
- `database/db.py`: Context-managed connection factory enforcing `PRAGMA foreign_keys = ON;`.
- `database/repository.py`: Parameterized Data Access Object (DAO) for atomic persistence of programs, compilation snapshots, token streams, error records, and artifacts.

---

## 4. User Interface Architecture (`app.py`)

- **Framework:** Streamlit (Python web framework).
- **Component Layout:**
  - **Dashboard:** Telemetry aggregation querying live SQLite counts.
  - **Code Analyzer:** Multiline script editor, sample selector, status pill, tabbed views for Tokens, AST, Symbol Table, TAC, and Errors.
  - **Token Analysis:** Data table with category multi-select filter and CSV export.
  - **Error Report:** Categorized list with line indicators and beginner remediation advice.
  - **Saved Programs:** CRUD management for user programs.
  - **Compilation History:** Historical audit trail with deep inspection.
  - **About & Viva Help:** Educational reference and oral exam preparation.

