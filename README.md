# Smart Multi-Language Compiler & Analyzer (C, Python, Java)

[![Python 3.11 | 3.12](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Frontend: Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red.svg)](https://streamlit.io/)
[![Database: SQLite3](https://img.shields.io/badge/Database-SQLite3-green.svg)](https://www.sqlite.org/)
[![Tests: pytest 59 passed](https://img.shields.io/badge/Tests-59%20Passed%20(100%25)-brightgreen.svg)](https://pytest.org/)
[![Languages: C, Python, Java](https://img.shields.io/badge/Languages-C%20%7C%20Python%20%7C%20Java-purple.svg)]()
[![Subject: Compiler Design](https://img.shields.io/badge/Course-5CS221PC%20TEC-orange.svg)]()

> **A Technical Enhancement Course (TEC) Mini-Project**  
> **Course:** Compiler Design (Subject Code: 5CS221PC)  
> **Degree:** B.E. Computer Science and Engineering (Third Year, Fifth Semester)  
> **Institution:** Shri Sant Gajanan Maharaj College of Engineering (SSGMCE), Shegaon  
> **Academic Session:** Autumn/Winter 2026–2027  

---

## 1. Project Overview

The **Smart Multi-Language Compiler & Analyzer** is a professional, educational compiler engineering workbench built with **Python 3.12**, **Streamlit**, and **SQLite**. It allows students and faculty to write, scan, parse, analyze, and execute source code across three major programming paradigms: **C**, **Python**, and **Java**.

The application features:
1. **Language-Specific Lexical Analyzers:** Independent tokenizers with 1-based spatial coordinate tracking (line and column numbers).
2. **Language-Specific Syntax Checkers:** Dedicated grammatical parsers enforcing language-specific rules (C recursive descent, Python AST indentation & block validation, and Java class/method parsing).
3. **Real Toolchain Compilation & Execution Adapters:**
   - **C:** Compiles via `gcc` or `clang` in an isolated subprocess.
   - **Python:** Validates syntax and executes via configured `python` interpreter with subprocess timeout protection.
   - **Java:** Compiles with `javac` and executes with `java` via installed JDK.
4. **Relational Persistence:** SQLite database (`compiler.db`) storing saved programs, execution runs, tokens, and errors with full foreign-key integrity.
5. **Interactive Web GUI:** Built with Streamlit, providing real-time telemetry, token inspection, AST visualization, TAC intermediate code generation, and execution output consoles.

---

## 2. Multi-Language Architecture

The system uses a decoupled architecture ensuring each language has its own dedicated lexer, parser, and execution adapter while sharing a unified diagnostic, token, and persistence contract:

```
compiler/
├── tokens.py               # Unified token definitions, types & keywords
├── diagnostics.py          # Centralized error reporting & CompilationResult
├── pipeline.py             # Unified multi-language compilation coordinator
├── ast_nodes.py            # Strongly-typed Abstract Syntax Tree nodes
├── semantic.py             # Symbol table manager & semantic checks
├── tac.py                  # Linearized Three-Address Code (TAC) generator
│
├── lexers/                 # Independent Lexical Analyzers
│   ├── base_lexer.py       # BaseLexer abstract interface
│   ├── c_lexer.py          # Full C scanner (keywords, preprocessor, comments, literals)
│   ├── python_lexer.py     # Python scanner (indent/dedent, colons, docstrings)
│   └── java_lexer.py       # Java scanner (class, annotations, methods, literals)
│
├── parsers/                # Independent Syntax Checkers
│   ├── base_parser.py      # BaseParser abstract interface
│   ├── c_parser.py         # C recursive-descent parser (functions, main, blocks)
│   ├── python_parser.py    # Python AST validator (indentation & syntax errors)
│   └── java_parser.py      # Java class & method structure parser
│
└── adapters/               # Real Compiler & Runtime Toolchains
    ├── base_adapter.py     # BaseExecutionAdapter interface
    ├── c_adapter.py        # GCC / Clang compilation & binary execution
    ├── python_adapter.py   # Isolated Python subprocess runner
    ├── java_adapter.py     # javac / java JDK compiler & bytecode runner
    └── manager.py          # ToolchainManager coordinator & tool detector
```

---

## 3. Supported Languages & Grammar Specifications

### A. C Language
- **Keywords:** `int`, `float`, `char`, `double`, `void`, `if`, `else`, `for`, `while`, `return`, `switch`, `case`, `break`, `continue`, `struct`, and educational `print`.
- **Constructs:** `#include` preprocessor directives, `int main() { ... }`, custom functions, variable declarations, assignments, arithmetic precedence (`* /` before `+ -`), block scoping `{ ... }`, and `printf(...)` / `print(...)`.
- **Error Diagnostics:** Missing semicolons (`SYN001`), unmatched braces/parentheses (`SYN002`), missing identifiers (`SYN003`), missing equals (`SYN004`).
- **Toolchain:** Compiles with **GCC** or **Clang** (`gcc -O2 source.c -o program.exe`). If missing, provides clear installation guidance for Windows (MinGW-w64).

### B. Python 3
- **Keywords:** `def`, `class`, `if`, `elif`, `else`, `for`, `while`, `return`, `import`, `from`, `try`, `except`, `finally`, `with`, `as`, `pass`, `break`, `continue`, `and`, `or`, `not`, `in`, `is`, `True`, `False`, `None`.
- **Constructs:** Variable assignments, expressions, functions, classes, imports, loops, `print(...)`.
- **Indentation:** Lexer tracks significant indentation, emitting `INDENT`, `DEDENT`, and `NEWLINE` tokens. Flags `IndentationError` when blocks are misaligned.
- **Error Diagnostics:** Missing colons (`SYN_PY_SYNTAX`), indentation errors (`SYN_PY_INDENT`), unclosed quotation marks.
- **Toolchain:** Executed directly via the active Python 3 interpreter in an isolated subprocess with 5.0-second timeout.

### C. Java
- **Keywords:** `class`, `public`, `private`, `protected`, `static`, `void`, `int`, `double`, `float`, `char`, `boolean`, `String`, `if`, `else`, `for`, `while`, `return`, `new`, `this`, `extends`, `implements`, `try`, `catch`, `finally`, `import`, `package`.
- **Constructs:** Class definitions (`public class Main`), `public static void main(String[] args)`, methods, variable declarations, assignments, `System.out.println(...)`, braces `{ ... }`, and semicolons `;`.
- **Student Sandbox Mode:** If raw statements without a class wrapper are submitted, the adapter wraps them in a `Main` class for testing.
- **Error Diagnostics:** Missing class declarations, unmatched braces, missing semicolons.
- **Toolchain:** Compiles with **javac** and executes with **java** via JDK.

---

## 4. Subprocess Security & Isolation

To protect system integrity when compiling user-provided source code:
- **Zero in-process execution:** User code is **never** executed using `eval()` or `exec()`.
- **Strict Timeouts:** Every compiler and execution process enforces a strict 5.0-second timeout to prevent infinite loops.
- **Temporary Working Directories:** Code is written and compiled in isolated temporary directories (`tempfile.TemporaryDirectory`) that are cleaned up automatically.
- **Output Capping:** Standard output and standard error streams are capped at 50 KB to prevent memory exhaustion from runaway print loops.
- **Credential Protection:** Application secrets and database URLs are explicitly stripped from child subprocess environments.

---

## 5. Sample Programs Included

The application includes 13 curated educational programs in `samples/sample_programs.json`:

| ID | Language | Description | Expected Output |
| :--- | :---: | :--- | :--- |
| `sample_c_01` | **C** | Standard C program with `printf` | Execution output: `30` |
| `sample_c_02` | **C** | Variable declarations & precedence | Tokenization, AST & TAC |
| `sample_c_03` | **C** | Missing semicolon | Syntax error `SYN001` |
| `sample_c_04` | **C** | Unmatched curly braces | Syntax error `SYN002` |
| `sample_py_01` | **Python** | Sum calculation and print | Execution output: `30` |
| `sample_py_02` | **Python** | Factorial function with loop | Execution output: `Factorial of 5 is 120` |
| `sample_py_03` | **Python** | Missing indentation under def | `IndentationError` |
| `sample_py_04` | **Python** | Missing colon on if statement | `SyntaxError: expected ':'` |
| `sample_java_01` | **Java** | `Main` class with `System.out.println` | Execution output: `30` |
| `sample_java_02` | **Java** | Java loop and method call | Execution output: `Sum 1 to 5: 15` |
| `sample_java_03` | **Java** | Missing semicolon in Java | Syntax error `SYN001` |
| `sample_java_04` | **Java** | Unclosed class brace | Syntax error `SYN_JAVA_002` |

---

## 6. Automated Testing (59 Tests — 100% Pass Rate)

Run the automated test suite with pytest:

```powershell
python -m pytest -v
```

### Test Suite Summary
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1
collected 59 items

tests/test_adapters.py::test_python_execution_output_30 PASSED           [  1%]
tests/test_adapters.py::test_java_compilation_and_execution_30 PASSED    [  3%]
tests/test_adapters.py::test_c_adapter_toolchain_reporting PASSED        [  5%]
tests/test_adapters.py::test_pipeline_with_execution_flag PASSED         [  6%]
tests/test_adapters.py::test_language_switching_in_pipeline PASSED       [  8%]
tests/test_c_lang.py (6 tests) PASSED                                    [ 18%]
tests/test_database.py (5 tests) PASSED                                  [ 27%]
tests/test_java_lang.py (5 tests) PASSED                                 [ 35%]
tests/test_lexer.py (9 tests) PASSED                                     [ 50%]
tests/test_parser.py (10 tests) PASSED                                   [ 67%]
tests/test_pipeline.py (4 tests) PASSED                                  [ 74%]
tests/test_python_lang.py (6 tests) PASSED                               [ 84%]
tests/test_semantic.py (5 tests) PASSED                                  [ 93%]
tests/test_tac.py (4 tests) PASSED                                       [100%]

============================= 59 passed in 1.53s ==============================
```

Detailed test logs are available in [`docs/test_results.md`](file:///c:/Users/ASUS/OneDrive/Desktop/CD%20Project/LexAnalyzer_CD/docs/test_results.md).

---

## 7. Installation & Execution Guide

### Windows PowerShell

```powershell
# 1. Navigate to project directory
cd "C:\Users\ASUS\OneDrive\Desktop\CD Project\LexAnalyzer_CD"

# 2. Upgrade pip and install requirements
python -m pip install --upgrade pip
pip install -r requirements.txt

# 3. Launch the Streamlit Web Application
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

---

## 8. College Submission Documentation

| Document | Location | Purpose |
| :--- | :--- | :--- |
| **Editable Word Report** | [`docs/TEC_Project_Report.docx`](file:///c:/Users/ASUS/OneDrive/Desktop/CD%20Project/LexAnalyzer_CD/docs/TEC_Project_Report.docx) | 12+ page formatted report with SSGMCE Shegaon cover page and chapters. |
| **Complete Markdown Report** | [`docs/report.md`](file:///c:/Users/ASUS/OneDrive/Desktop/CD%20Project/LexAnalyzer_CD/docs/report.md) | Academic report in markdown format. |
| **Viva Defense Guide** | [`docs/viva_questions.md`](file:///c:/Users/ASUS/OneDrive/Desktop/CD%20Project/LexAnalyzer_CD/docs/viva_questions.md) | Comprehensive viva questions and model answers. |
| **Test Results** | [`docs/test_results.md`](file:///c:/Users/ASUS/OneDrive/Desktop/CD%20Project/LexAnalyzer_CD/docs/test_results.md) | Full 59 test execution results log. |
| **Grammar Reference** | [`docs/grammar.md`](file:///c:/Users/ASUS/OneDrive/Desktop/CD%20Project/LexAnalyzer_CD/docs/grammar.md) | EBNF grammar specifications. |
| **Database Schema** | [`docs/database_schema.md`](file:///c:/Users/ASUS/OneDrive/Desktop/CD%20Project/LexAnalyzer_CD/docs/database_schema.md) | SQLite schema data dictionary and ER diagram. |

---

## 9. Git Repository Upload Instructions

```powershell
# 1. Stage all project files
git add .

# 2. Commit the upgrade
git commit -m "Upgrade to Multi-Language Mini Compiler (C, Python, Java) with Toolchains"

# 3. Push to your GitHub repository
# git push origin main
```
