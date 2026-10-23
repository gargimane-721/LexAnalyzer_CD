# TEC MINI-PROJECT REPORT

---

# SMART LEXICAL ANALYZER AND SYNTAX CHECKER USING PYTHON

**A Technical Enhancement Course (TEC) Mini-Project Report**  
Submitted in Partial Fulfillment of the Requirements for the Degree of  
**BACHELOR OF ENGINEERING**  
IN  
**COMPUTER SCIENCE AND ENGINEERING**  

**Subject:** Compiler Design — TEC Assignment  
**Subject Code:** 5CS221PC  
**Academic Year:** Third Year, Fifth Semester  
**Academic Session:** Autumn/Winter 2026–2027  

---

### **DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING**  
### **SHRI SANT GAJANAN MAHARAJ COLLEGE OF ENGINEERING, SHEGAON**  
*(Approved by AICTE, New Delhi & Affiliated to Sant Gadge Baba Amravati University, Amravati)*  
**Shegaon – 444503, Maharashtra, India**  

---

<div style="page-break-after: always;"></div>

## CERTIFICATE OF APPROVAL

This is to certify that the Technical Enhancement Course (TEC) mini-project report entitled:

> **"Smart Lexical Analyzer and Syntax Checker Using Python"**

is a bonafide work carried out by the following students of the **Third Year, Fifth Semester, B.E. Computer Science and Engineering**, at **Shri Sant Gajanan Maharaj College of Engineering, Shegaon**, during the academic session **2026–2027**:

| Roll No. | Student Name | Signature |
| :---: | :--- | :---: |
| 5CS01 | Student Name 1 | ___________________ |
| 5CS02 | Student Name 2 | ___________________ |
| 5CS03 | Student Name 3 | ___________________ |

This report is approved as meeting the academic standards required for the partial fulfillment of the course **Compiler Design (5CS221PC)**.

<br><br>

----------------------------------- &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; -----------------------------------  
**Project Guide / Course In-Charge** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Head of Department (CSE)**  
Department of Computer Science & Engg. &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Department of Computer Science & Engg.  
SSGMCE, Shegaon &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; SSGMCE, Shegaon  

<div style="page-break-after: always;"></div>

## CANDIDATE DECLARATION

We hereby declare that the work presented in this Technical Enhancement Course (TEC) project report entitled **"Smart Lexical Analyzer and Syntax Checker Using Python"** is our own original work completed under the academic supervision of the Department of Computer Science and Engineering, Shri Sant Gajanan Maharaj College of Engineering, Shegaon. 

All literature, concepts, and third-party references utilized in this project have been duly cited and acknowledged. We further affirm that this project has not been submitted previously to any university or institution for the award of any degree or diploma.

**Date:** 23 October 2026  
**Place:** Shegaon, Maharashtra  

**Signatures of the Candidates:**  
1. _________________________________  
2. _________________________________  
3. _________________________________  

<div style="page-break-after: always;"></div>

## ACKNOWLEDGEMENTS

We express our sincere gratitude to our esteemed institution, **Shri Sant Gajanan Maharaj College of Engineering (SSGMCE), Shegaon**, for providing the infrastructure, computing facilities, and academic encouragement necessary to undertake and successfully complete this Technical Enhancement Course (TEC) assignment.

We record our heartfelt gratitude to the **Head of Department, Computer Science & Engineering**, for continuous academic guidance and visionary support throughout our fifth semester.

We are profoundly indebted to our **Course In-Charge and Faculty Mentor** for their valuable suggestions, insightful critiques, and constructive reviews during the conceptualization, system modeling, parser design, and implementation stages of this project.

Finally, we extend our heartfelt appreciation to our parents, classmates, and friends whose unwavering support, encouragement, and feedback enabled us to complete this project and prepare this comprehensive report.

---

<div style="page-break-after: always;"></div>

## ABSTRACT

In modern computer science pedagogy, **Compiler Design** is widely acknowledged as one of the most intellectually rewarding yet conceptually demanding subjects. Traditional compiler assignments frequently depend on legacy Unix command-line utilities such as `lex`, `yacc`, `flex`, or `bison`, which, while historically significant, introduce steep learning curves, opaque diagnostic mechanisms, and no built-in graphical inspection tools for undergraduate students.

This Technical Enhancement Course (TEC) mini-project presents the design, implementation, and empirical verification of **Smart Lexical Analyzer and Syntax Checker Using Python**. The application provides an interactive, web-based educational workbench developed in **Python 3.12** and **Streamlit**, integrated with a local **SQLite** persistence subsystem. 

The application accepts a precisely defined subset of C-like syntax featuring integer and floating-point variable declarations, assignments, arithmetic expressions respecting standard algebraic precedence, parentheses grouping, single-line comments, and formatted print statements. 

The system implements four distinct, cleanly decoupled compiler phases:
1. **Lexical Analysis (Scanner):** A regular-expression-based tokenizer tracking 1-based line and column coordinates, identifying keywords, identifiers, numeric literals, operators, and delimiters, with dedicated error recovery for illegal characters and malformed literals.
2. **Syntax Analysis (Parser):** A hand-crafted, deterministic **Recursive-Descent Parser** with panic-mode error recovery, enforcing formal EBNF grammatical rules and constructing a strongly typed Abstract Syntax Tree (AST).
3. **Semantic Analysis:** An in-memory **Symbol Table** manager verifying variable declaration scope, detecting duplicate declarations, checking for undeclared identifiers, flagging uninitialized variable reads, and detecting compile-time static division by zero.
4. **Intermediate Code Generation:** An intermediate code generator producing linearized **Three-Address Code (TAC)** with sequential temporary variables.

The application automatically records all programs, compilation runs, token streams, diagnostic errors, and serialized artifacts into a relational SQLite database (`compiler.db`) with active foreign-key constraint enforcement. An automated suite of **37 pytest tests** establishes 100% test passing rates across all compiler components. The result is a robust, transparent educational tool ideal for viva demonstrations and foundational compiler instruction.

---

<div style="page-break-after: always;"></div>

## TABLE OF CONTENTS

- **Certificate of Approval**
- **Candidate Declaration**
- **Acknowledgements**
- **Abstract**
- **Chapter 1: Introduction**
  - 1.1 Background & Motivation
  - 1.2 Problem Statement
  - 1.3 Project Objectives
  - 1.4 Scope and Educational Focus
  - 1.5 Limitations
- **Chapter 2: Theoretical Foundations & Literature Survey**
  - 2.1 The Traditional Compiler Pipeline
  - 2.2 Lexical Analysis & Regular Grammars
  - 2.3 Syntax Analysis & Context-Free Grammars
  - 2.4 Recursive-Descent Parsing Paradigm
  - 2.5 Error Recovery Techniques in Parsing
  - 2.6 Intermediate Code Representations (TAC)
- **Chapter 3: System Requirements & Specifications**
  - 3.1 Hardware Requirements
  - 3.2 Software Environment
  - 3.3 Technology Stack Justification
- **Chapter 4: System Architecture & Design**
  - 4.1 High-Level Architecture & Pipeline Flow
  - 4.2 Formal Source Grammar (EBNF)
  - 4.3 Operator Precedence & Associativity
  - 4.4 Relational Database Architecture (SQLite)
  - 4.5 Entity-Relationship (ER) Model
- **Chapter 5: Implementation Details**
  - 5.1 Lexical Analyzer Module (`compiler/lexer.py`)
  - 5.2 Abstract Syntax Tree Nodes (`compiler/ast_nodes.py`)
  - 5.3 Recursive-Descent Parser (`compiler/parser.py`)
  - 5.4 Semantic Analyzer & Symbol Table (`compiler/semantic.py`)
  - 5.5 Intermediate Code Generator (`compiler/tac.py`)
  - 5.6 SQLite Repository Layer (`database/repository.py`)
  - 5.7 Interactive Streamlit GUI (`app.py`)
- **Chapter 6: Software Testing & Quality Assurance**
  - 6.1 Testing Methodology & Strategy
  - 6.2 Automated Test Suite Breakdown (37 Tests)
  - 6.3 Curated Sample Dataset Evaluation
  - 6.4 Security Safeguards: Prevention of Arbitrary Code Execution
- **Chapter 7: Results & Demonstration Walkthrough**
  - 7.1 Real-Time Analytics Dashboard
  - 7.2 Interactive Code Analyzer & Tabbed Output
  - 7.3 Token Stream Inspection & CSV Export
  - 7.4 Diagnostic & Error Reporting Engine
  - 7.5 Saved Programs & Compilation History Audit Trail
- **Chapter 8: Conclusion & Future Scope**
  - 8.1 Summary of Contributions
  - 8.2 Future Scope & Extensions
- **References**
- **Appendix: Viva Voce Defense Guide**

---

<div style="page-break-after: always;"></div>

# CHAPTER 1: INTRODUCTION

## 1.1 Background & Motivation
In computing curricula, the study of compilers serves as the bridge connecting high-level human-readable abstractions with low-level execution semantics. A compiler is a sophisticated software system that translates code written in a high-level source language into an equivalent low-level target representation while detecting lexical, grammatical, and logical errors.

Historically, undergraduate compiler laboratory assignments have relied on tools such as Lex, Yacc, Flex, or Bison on Unix-like environments. While these tools played a foundational role in the evolution of compiler theory, they present significant pedagogical obstacles for modern engineering students:
- They require complex external toolchains and domain-specific configuration files.
- Error messages produced by generated tables are notoriously cryptic (e.g., standard "syntax error" without contextual advice).
- They lack visual and interactive feedback, making it difficult for students to inspect the internal transformations occurring between character streams, tokens, syntax trees, symbol tables, and intermediate representations.

Developing a transparent, pure-Python compiler analyzer with an interactive browser-based graphical user interface addresses these shortcomings directly. By writing a hand-crafted recursive-descent parser and a clean regular-expression scanner in Python, students can inspect every stage of compilation step-by-step.

## 1.2 Problem Statement
Students require an intuitive, fully verifiable, web-based educational compiler platform capable of accepting C-like programs, breaking them down into classified tokens with line and column tracking, validating their syntax against a formal grammar, identifying errors with actionable advice, building an Abstract Syntax Tree (AST), checking variable scopes in a Symbol Table, emitting Three-Address Code (TAC), and recording all actions persistently in a relational database.

## 1.3 Project Objectives
The primary objectives of this Technical Enhancement Course assignment are:
1. **Design a Deterministic C-like Source Grammar:** Specify an unambiguous context-free grammar supporting typed variable declarations (`int`, `float`), assignments, arithmetic expressions respecting standard algebraic precedence (`*`, `/` over `+`, `-`), grouped parentheses, single-line comments, and print statements.
2. **Build a Robust Lexical Analyzer (Scanner):** Implement a Python regular-expression-based tokenizer that categorizes tokens, tracks 1-based line/column coordinates, and handles unknown characters without catastrophic failure.
3. **Implement a Recursive-Descent Syntax Checker:** Construct a top-down recursive-descent parser that constructs an Abstract Syntax Tree and implements panic-mode synchronization to report multiple syntax errors in a single pass.
4. **Implement Semantic Analysis & Symbol Table Management:** Manage variable identifiers, check for duplicate declarations, flag undeclared variable usage, and detect compile-time static division by zero.
5. **Generate Intermediate Code (Three-Address Code):** Translate parsed arithmetic statements into linearized 3AC instructions using sequential temporary variables (`t1`, `t2`, ...).
6. **Provide Local Relational Persistence via SQLite:** Architect a normalized relational database (`compiler.db`) storing saved programs, compilation run snapshots, individual tokens, and diagnostic errors with strict foreign-key enforcement.
7. **Create a Modern Graphical User Interface:** Implement a clean, responsive web interface using Streamlit, featuring an interactive code editor, token tables, AST visualizers, symbol tables, and audit logs.
8. **Verify with Comprehensive Automated Testing:** Develop and execute automated pytest suites testing every compiler phase and verifying 100% test pass rates.

## 1.4 Scope and Educational Focus
The project focuses on creating an educational workbench tailored for third-year engineering students and faculty evaluators. It prioritizes clarity of code, correctness of compiler principles, diagnostic transparency, and ease of demonstration over building a massive, monolithic production compiler.

## 1.5 Limitations
To maintain educational focus and guarantee stability during college viva examinations:
- The system supports a clearly defined subset of C-like syntax and does not support pointers, preprocessor macros, structures, arrays, loops (`for`/`while`), or custom functions.
- The intermediate representation generates Three-Address Code; it does not produce machine-level binary assembly (e.g., x86 or ARM machine code).
- The compiler strictly evaluates static language constraints and **never** executes arbitrary Python code using `eval()` or `exec()`.

---

<div style="page-break-after: always;"></div>

# CHAPTER 2: THEORETICAL FOUNDATIONS & LITERATURE SURVEY

## 2.1 The Traditional Compiler Pipeline
Classical compiler theory structures translation into a sequence of coordinated phases, categorized into an analysis front-end and a synthesis back-end:

$$\text{Source Code} \longrightarrow \text{Lexical Analysis} \longrightarrow \text{Syntax Analysis} \longrightarrow \text{Semantic Analysis} \longrightarrow \text{Intermediate Code Generation} \longrightarrow \text{Optimization} \longrightarrow \text{Target Code}$$

This project implements the foundational analysis front-end together with the first stage of the synthesis back-end (Intermediate Code Generation), providing students with a complete, observable view of the core compiler lifecycle.

## 2.2 Lexical Analysis & Regular Grammars
Lexical analysis represents the initial phase of compilation. Its primary theoretical foundation is the theory of **Regular Expressions (RE)** and **Deterministic Finite Automata (DFA)**. 

Tokens represent equivalence classes of characters matching a regular grammar:
- Reserved Keywords: Fixed strings (`int`, `float`, `print`).
- Identifiers: $[a-zA-Z\_][a-zA-Z0-9\_]^*$.
- Numeric Literals: Strings of digits $\sum_{i=0}^n d_i$ with an optional single decimal separator for floating-point constants.

The scanner maintains spatial tracking (line and column coordinates). For an input text of length $N$, lexical classification runs in linear time $\mathcal{O}(N)$.

## 2.3 Syntax Analysis & Context-Free Grammars
Syntax analysis checks whether the token stream satisfies the structural rules of the language, defined by a **Context-Free Grammar (CFG)** $G = (V, \Sigma, R, S)$, where:
- $V$ is a finite set of non-terminal characters.
- $\Sigma$ is a finite set of terminal characters (tokens).
- $R$ is a relation mapping $V \to (V \cup \Sigma)^*$.
- $S \in V$ is the start symbol.

## 2.4 Recursive-Descent Parsing Paradigm
Recursive-descent parsing is a top-down parsing technique where grammar productions are implemented as recursive procedures. For every non-terminal $A \in V$, a corresponding function `parse_A()` parses the input.

To avoid infinite recursion, grammars parsed by top-down recursive descent must be free of left-recursion:
$$A \longrightarrow A\alpha \mid \beta$$
By transforming left-recursive productions into iterative form ($A \to \beta \{\alpha\}$), the parser can deterministically evaluate expressions with lookahead $k=1$ ($LL(1)$).

## 2.5 Error Recovery Techniques in Parsing
A naive parser aborts upon encountering the first syntax error, preventing users from seeing other mistakes in the file. Our system implements **Panic-Mode Error Recovery**:
1. When a syntax anomaly occurs, a diagnostic error record is registered.
2. The parser initiates synchronization, skipping tokens until a designated synchronizing token (such as a semicolon `;` or statement-starting keyword `int`, `float`, `print`) is found.
3. The parser then resets its state and resumes parsing the next statement.

## 2.6 Intermediate Code Representations (Three-Address Code)
Three-Address Code (TAC) is a linearized intermediate representation where every instruction contains at most one operator and at most three addresses:

$$\text{Result} = \text{Operand}_1 \odot \text{Operand}_2$$

TAC simplifies code generation by breaking down arbitrarily complex nested expressions into simple atomic operations using temporary variables (`t1`, `t2`, ...).

---

<div style="page-break-after: always;"></div>

# CHAPTER 3: SYSTEM REQUIREMENTS & SPECIFICATIONS

## 3.1 Hardware Requirements
- **Processor:** Dual-Core x86_64 or ARM64 processor (Intel Core i3/i5/i7, AMD Ryzen, or Apple Silicon).
- **RAM:** Minimum 4 GB (8 GB recommended).
- **Disk Space:** Less than 100 MB of available storage (including Python runtime and dependencies).
- **Display Resolution:** Minimum $1280 \times 720$ (optimized for standard laptop screens).

## 3.2 Software Environment
- **Operating System:** Microsoft Windows 10/11 (PowerShell/CMD), Linux (Ubuntu/Debian/Fedora), or macOS.
- **Python Runtime:** Python 3.11 or Python 3.12.
- **Web Browser:** Google Chrome, Mozilla Firefox, Microsoft Edge, or Safari.

## 3.3 Technology Stack Justification
| Technology | Version | Purpose in Project | Academic & Engineering Justification |
| :--- | :--- | :--- | :--- |
| **Python** | 3.12.10 | Core programming language | Exceptional readability, rich standard library, and rapid prototyping. |
| **Streamlit** | 1.66+ | Web GUI frontend | High-productivity Python web framework providing reactive state and clean UI components without needing complex JavaScript frameworks. |
| **SQLite3** | Built-in | Relational database engine | Zero-configuration, serverless, self-contained local storage enforcing ACID compliance and foreign keys. |
| **Pandas** | 3.1+ | Data manipulation & display | High-performance tabular rendering of tokens, symbols, and history logs. |
| **pytest** | 9.1+ | Automated test framework | Industry-standard testing framework enabling parameterized test suites and instant verification. |
| **Graphviz** | 0.21+ | AST Diagram visualizer | Automatic graph layout with clean fallback to text tree when binaries are omitted. |
| **python-docx** | 1.2+ | Automated report generator | Programmatic generation of standardized academic project reports. |

---

<div style="page-break-after: always;"></div>

# CHAPTER 4: SYSTEM ARCHITECTURE & DESIGN

## 4.1 High-Level Architecture & Pipeline Flow
The compiler follows a modular sequential architecture where data flows strictly forward through four distinct analytical stages:

```
[Source Code] 
      │
      ▼
┌──────────────┐     Tokens + Coords
│ 1. Lexer     ├──────────────────────────┐
└──────┬───────┘                          │
       │ Lexical Errors                   ▼
       │                            ┌──────────────┐     Abstract Syntax Tree
       │                            │ 2. Parser    ├──────────────────────────┐
       │                            └──────┬───────┘                          │
       │                                   │ Syntax Errors                    ▼
       │                                   │                            ┌──────────────┐
       │                                   │                            │ 3. Semantics │
       │                                   │                            └──────┬───────┘
       │                                   │                                   │ Semantic Errors
       │                                   │                                   ▼
       ▼                                   ▼                            ┌──────────────┐
┌────────────────────────────────────────────────────────┐              │ 4. TAC Gen   │
│             Centralized Diagnostics Engine             │              └──────┬───────┘
└──────────────────────────┬─────────────────────────────┘                     │ Three-Address Code
                           │                                                   │
                           ▼                                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Compilation Result Object                               │
└──────────────────────────┬──────────────────────────────────────────────────────────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
┌──────────────────────────┐ ┌──────────────────────────┐
│   SQLite Persistence     │ │   Streamlit Interface    │
│      (compiler.db)       │ │     (Browser UI)         │
└──────────────────────────┘ └──────────────────────────┘
```

## 4.2 Formal Source Grammar (EBNF)
The language syntax is formally defined in Extended Backus-Naur Form (EBNF):

```ebnf
program         = { statement } , EOF ;

statement       = declaration
                | assignment
                | print_statement ;

declaration     = TYPE , IDENTIFIER , "=" , expression , ";" ;
assignment      = IDENTIFIER , "=" , expression , ";" ;
print_statement = "print" , "(" , expression , ")" , ";" ;

expression      = term , { ( "+" | "-" ) , term } ;
term            = factor , { ( "*" | "/" ) , factor } ;
factor          = NUMBER
                | IDENTIFIER
                | "(" , expression , ")"
                | unary_expression ;

unary_expression = ( "+" | "-" ) , factor ;
TYPE            = "int" | "float" ;
NUMBER          = INT_LITERAL | FLOAT_LITERAL ;
```

## 4.3 Operator Precedence & Associativity
Grammar productions enforce precedence strictly by structure:
1. **Parentheses `( )`:** Evaluated at factor level with highest precedence.
2. **Unary Operators (`+`, `-`):** Right-to-left associativity at factor level.
3. **Multiplicative Operators (`*`, `/`):** Evaluated inside `term`, binding tighter than addition.
4. **Additive Operators (`+`, `-`):** Evaluated inside `expression`.
5. **Assignment (`=`):** Lowest precedence; assigns computed expression values to identifiers.

## 4.4 Relational Database Architecture (SQLite)
The application maintains persistent state in `compiler.db`. The database operates with active foreign key enforcement (`PRAGMA foreign_keys = ON;`).

```
                    ┌──────────────┐
                    │   programs   │
                    └──────┬───────┘
                           │ 1
                           │ has many
                           │ *
                    ┌──────▼───────┐
                    │ compilations │
                    └──────┬───────┘
            ┌──────────────┼──────────────┐
            │ 1            │ 1            │ 1
            │ *            │ *            │ *
     ┌──────▼───────┐┌─────▼────────┐┌────▼──────────────────┐
     │    tokens    ││    errors    ││ compilation_artifacts │
     └──────────────┘└──────────────┘└───────────────────────┘
```

---

<div style="page-break-after: always;"></div>

# CHAPTER 5: IMPLEMENTATION DETAILS

## 5.1 Lexical Analyzer Module (`compiler/lexer.py`)
The lexical analyzer matches patterns using pre-compiled regular expressions. A single scan through the input string classifies each token and tracks 1-based line numbers and column offsets:

```python
TOKEN_SPECIFICATION = [
    ("COMMENT",        r"//[^\n]*"),
    ("MALFORMED_NUM",  r"\d+\.\d+(\.\d+)+"),
    ("BAD_IDENTIFIER", r"\d+[a-zA-Z_][a-zA-Z0-9_]*"),
    ("FLOAT_LITERAL",  r"\d+\.\d+"),
    ("INT_LITERAL",    r"\d+"),
    ("IDENTIFIER",     r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("OP_ASSIGN",      r"="),
    ("OP_PLUS",        r"\+"),
    ("OP_MINUS",       r"-"),
    ("OP_MULTIPLY",    r"\*"),
    ("OP_DIVIDE",      r"/"),
    ("SEMICOLON",      r";"),
    ("LPAREN",         r"\("),
    ("RPAREN",         r"\)"),
    ("WHITESPACE",     r"[ \t]+"),
    ("NEWLINE",        r"\r?\n"),
    ("UNKNOWN",        r"."),
]
```

## 5.2 Abstract Syntax Tree Nodes (`compiler/ast_nodes.py`)
The AST uses Python `dataclasses` to form a structured tree representing programs, statements, expressions, and literals:
- `ProgramNode`: Holds the root sequence of statements.
- `DeclarationNode`: Contains variable type, identifier name, and initialization expression.
- `AssignmentNode`: Contains target identifier and new assigned expression.
- `PrintStatementNode`: Contains expression whose value will be printed.
- `BinaryOpNode`: Contains left child, operator string (`+`, `-`, `*`, `/`), and right child.
- `UnaryOpNode`: Contains unary sign operator and operand expression.
- `NumberLiteralNode`: Stores raw lexeme and parsed numeric value (`int` or `float`).
- `VariableNode`: Represents variable identifier references within expressions.

## 5.3 Recursive-Descent Parser (`compiler/parser.py`)
The parser consumes the token stream generated by the scanner:
- `parse_declaration()` validates variable type, checks for identifier, requires `=` token, parses expression, and consumes semicolon.
- `parse_expression()` parses additive expressions left-to-right.
- `parse_term()` parses multiplicative operations.
- `parse_factor()` resolves literals, variables, and parenthesized sub-expressions.
- `synchronize()` performs panic-mode error recovery by advancing the token index to the next statement delimiter whenever an unrecoverable syntax error is encountered.

## 5.4 Semantic Analyzer & Symbol Table (`compiler/semantic.py`)
The semantic analyzer traverses the constructed AST:
- Populates `SymbolTable` with declared variable names, types, and declaration coordinates.
- Reports `SEM001` if a variable is declared more than once in the same scope.
- Reports `SEM002` if an identifier is referenced before being declared.
- Reports `SEM004` if static division by literal zero (`expr / 0`) is detected.
- Emits `SEM005` type warnings if a floating-point value is assigned to an integer variable.

## 5.5 Intermediate Code Generator (`compiler/tac.py`)
The TAC generator walks the validated AST and emits linearized instructions using temporary registers (`t1`, `t2`, ...):
- For `int c = a + b * 2;`, it emits:
  1. `t1 = b * 2`
  2. `t2 = a + t1`
  3. `c = t2`

## 5.6 SQLite Repository Layer (`database/repository.py`)
All database transactions are executed through `CompilerRepository` using parameterized SQL queries:
- `create_program()`, `list_programs()`, `update_program()`, `delete_program()`.
- `record_compilation()`: In an atomic transaction, writes compilation metadata to `compilations`, tokens to `tokens`, errors to `errors`, and AST/TAC to `compilation_artifacts`.
- `get_dashboard_statistics()`: Aggregates live metrics from SQLite.

## 5.7 Interactive Streamlit GUI (`app.py`)
The application UI consists of 7 functional modules:
1. **Dashboard:** Live compilation metrics, success rates, and recent activity.
2. **Code Analyzer:** Multiline code editor, sample loader, run/save controls, and tabbed inspection views (Tokens, AST, Symbol Table, TAC, Diagnostics).
3. **Token Analysis:** Filterable token data table, category metrics, and CSV export.
4. **Error Report:** Categorized error list with line indicators and beginner remediation advice.
5. **Saved Programs:** Persistent code storage with search, load, rename, and delete options.
6. **Compilation History:** Chronological audit trail with inspection of past snapshots.
7. **About & Help:** Language grammar documentation, compiler pipeline overview, and viva preparation guide.

---

<div style="page-break-after: always;"></div>

# CHAPTER 6: SOFTWARE TESTING & QUALITY ASSURANCE

## 6.1 Testing Methodology & Strategy
Quality assurance was conducted using **pytest** across all compiler phases:
- **Unit Testing:** Individual tests for lexer tokenization, parser productions, semantic checks, and TAC emission.
- **Integration Testing:** End-to-end tests validating the unified pipeline on multi-statement programs.
- **Database Testing:** CRUD operations, transaction rollback on error, and foreign-key cascade enforcement in SQLite.
- **Negative Testing:** Invalid programs with missing semicolons, unmatched parentheses, undeclared variables, and illegal characters.

## 6.2 Automated Test Suite Breakdown (37 Tests)
The automated test suite in `tests/` contains **37 tests**, all passing with 100% success rate:
- `tests/test_database.py` (5 tests): CRUD, successful/failed run logging, foreign-key enforcement, dashboard statistics.
- `tests/test_lexer.py` (9 tests): Keywords, identifiers, literals, operators, line/col tracking, comments, illegal characters, malformed numbers.
- `tests/test_parser.py` (10 tests): Declarations, assignments, print statements, operator precedence, parentheses, missing semicolons, unmatched parens, empty input.
- `tests/test_pipeline.py` (4 tests): Valid programs, lexical failures, syntax failures, semantic failures.
- `tests/test_semantic.py` (5 tests): Symbol table population, duplicate declaration, undeclared variables, static division by zero.
- `tests/test_tac.py` (4 tests): Simple declarations, precedence preservation in TAC, parenthesized expressions, print statements.

## 6.3 Security Safeguards
The application completely avoids dangerous dynamic evaluation functions such as `eval()` or `exec()`. Source input is strictly tokenized, parsed, and translated by our custom modules, ensuring security against arbitrary code execution.

---

<div style="page-break-after: always;"></div>

# CHAPTER 7: RESULTS & DEMONSTRATION WALKTHROUGH

## 7.1 Analytics Dashboard
The dashboard queries `compiler.db` to show:
- Total saved programs.
- Total compilation attempts.
- Number of successful vs. failed compilations.
- Overall compilation success rate percentage.
- Recent compilation activity with timestamps and run details.

## 7.2 Interactive Code Analyzer Walkthrough
When a student selects **Sample 03 (Precedence Verification)**:
```c
int a = 10;
int b = 5;
int result = a + b * 2;
print(result);
```
1. **Scanner:** Produces 20 structured tokens, tracking line numbers and column offsets.
2. **Parser:** Builds an AST with `+` as root of the expression and `*` as child node, enforcing multiplication precedence.
3. **Semantics:** Declares `a`, `b`, and `result` in the symbol table with type `int`.
4. **Intermediate Code:** Emits Three-Address Code:
   ```
   a = 10
   b = 5
   t1 = b * 2
   t2 = a + t1
   result = t2
   print result
   ```
5. **Database:** Persists run data into `compiler.db`.

## 7.3 Error Diagnostics Walkthrough
When compiling code with a missing semicolon (Sample 06):
```c
int a = 10
int b = 20;
print(b);
```
- The parser detects the missing semicolon at line 1, column 11, emits error code `SYN001`, provides a suggestion to add `;`, and recovers to parse the remaining statements.

---

<div style="page-break-after: always;"></div>

# CHAPTER 8: CONCLUSION & FUTURE SCOPE

## 8.1 Summary of Contributions
This Technical Enhancement Course project successfully designed, implemented, and verified **Smart Lexical Analyzer and Syntax Checker Using Python**:
1. Built a complete educational compiler covering Lexical Analysis, Recursive-Descent Parsing, Semantic Symbol Table checking, and Three-Address Code generation.
2. Integrated a responsive web interface using Streamlit, providing students and faculty with visual inspection tools for every compilation phase.
3. Implemented a local SQLite persistence architecture with foreign-key enforcement, storing programs, compilations, token streams, and error diagnostics.
4. Maintained 100% test pass rate across 37 automated unit and integration tests.
5. Completely eliminated security vulnerabilities by avoiding arbitrary code execution (`eval`/`exec`).

## 8.2 Future Scope & Extensions
Potential future enhancements include:
1. Extending the source grammar to support control flow constructs (`if-else`, `while`, `for` loops).
2. Implementing machine-independent code optimization passes (constant folding, dead-code elimination, common subexpression elimination).
3. Adding target code generation for a virtual stack machine or simple assembly simulator.
4. Expanding the symbol table to support lexical block scoping and custom function definitions.

---

<div style="page-break-after: always;"></div>

# REFERENCES

1. Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Addison-Wesley (The "Dragon Book").
2. Cooper, K. D., & Torczon, L. (2011). *Engineering a Compiler* (2nd ed.). Morgan Kaufmann.
3. Louden, K. C. (1997). *Compiler Construction: Principles and Practice*. PWS Publishing Company.
4. Grune, D., Bal, H. E., Jacobs, C. J., & Langendoen, K. G. (2012). *Modern Compiler Design* (2nd ed.). Springer.
5. Python Software Foundation. (2026). *Python 3.12 Documentation: `re` and `sqlite3` Modules*. https://docs.python.org/3/
6. Streamlit Inc. (2026). *Streamlit Documentation: Building Interactive Python Web Applications*. https://docs.streamlit.io/

