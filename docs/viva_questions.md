# Comprehensive Viva & Oral Defense Preparation Guide

**Project Title:** Smart Lexical Analyzer and Syntax Checker Using Python  
**Course:** Compiler Design — TEC Assignment (5CS221PC)  
**Department:** Computer Science & Engineering  
**College:** Shri Sant Gajanan Maharaj College of Engineering, Shegaon  

---

## Category 1: Lexical Analysis (Scanner)

### Q1. What is the role of a Lexical Analyzer in a compiler pipeline?
**Answer:**  
The lexical analyzer (or scanner) is the first phase of the compiler. It reads the source program as a raw stream of characters, groups them into meaningful minimal syntactic units called **lexemes**, classifies them into predefined **tokens** (e.g., Keywords, Identifiers, Literals, Operators, Separators), strips out whitespace and comments, and tracks source code coordinates (line and column numbers) for error reporting.

### Q2. What is the difference between a Token, a Lexeme, and a Pattern?
**Answer:**  
- **Token:** An abstract category or category-value pair assigned by the compiler (e.g., `IDENTIFIER`, `INT_LITERAL`, `OP_PLUS`).
- **Lexeme:** The actual concrete substring in the source code matching a pattern (e.g., `counter`, `42`, `+`).
- **Pattern:** The formal rule or regular expression defining what characters may constitute a valid token (e.g., `[a-zA-Z_][a-zA-Z0-9_]*` for identifiers).

### Q3. How does your lexer prevent confusing a keyword like `int` with an identifier like `integerValue`?
**Answer:**  
Our lexer scans full words using the identifier pattern `[a-zA-Z_][a-zA-Z0-9_]*`. Once the entire word is matched as a maximal sequence, the lexer checks if the lexeme exists in the reserved `KEYWORDS` dictionary. If the lexeme is exactly `"int"`, it returns `KEYWORD_INT`; otherwise, it returns `IDENTIFIER`. This prevents prefix-matching mistakes.

### Q4. How does the scanner handle unsupported characters like `@` or `$`?
**Answer:**  
Rather than crashing the entire application with an unhandled exception, our lexer appends an `UNKNOWN` token to the stream and records a structured diagnostic (`LEX001`). It then advances by one character and continues scanning. This allows the compiler to detect and display all lexical errors in a single pass.

### Q5. What is the time complexity of the lexical analysis phase?
**Answer:**  
The scanner operates in linear time $\mathcal{O}(N)$, where $N$ is the total number of characters in the source code, as each character is examined a constant number of times using regular expression matching.

---

## Category 2: Syntax Analysis (Parser)

### Q6. What type of parser is implemented in this project?
**Answer:**  
We implemented a hand-written **Top-Down Recursive-Descent Parser** with $k=1$ lookahead (an `LL(1)` grammar subset). Each non-terminal grammar rule is mapped to a dedicated Python method (e.g., `parse_declaration`, `parse_expression`, `parse_term`, `parse_factor`).

### Q7. Why did you choose Recursive-Descent over tools like Lex/Yacc or PLY?
**Answer:**  
Recursive-descent parsers are clean, transparent, require no external compiler-compiler build step, and allow precise error messages and custom error synchronization. They are beginner-friendly and ideal for demonstrating compiler engineering concepts in an academic setting.

### Q8. How does the parser enforce operator precedence without an external table?
**Answer:**  
Precedence is encoded directly into the grammar's call hierarchy:
1. `parse_expression()` handles low-precedence additive operators (`+`, `-`).
2. `parse_term()` handles medium-precedence multiplicative operators (`*`, `/`).
3. `parse_factor()` handles highest-precedence primary elements: literals, identifiers, unary operators, and parenthesized expressions `(...)`.
Because `parse_term()` is called before handling `+` or `-`, `*` and `/` sub-trees are constructed deeper in the AST, guaranteeing they evaluate first.

### Q9. How is associativity handled in expressions like `a - b - c`?
**Answer:**  
Left-associativity is handled using a `while` loop within `parse_expression()` and `parse_term()`. As operators are encountered left-to-right, the existing expression becomes the `left` child of a new `BinaryOpNode`, producing left-branching trees: `((a - b) - c)`.

### Q10. What is Error Recovery (Panic-Mode Synchronization)?
**Answer:**  
When the parser encounters an unexpected token (e.g., missing semicolon), raising a fatal crash would halt compilation. In our parser, after logging the syntax diagnostic (`SYN001`), the `synchronize()` method discards invalid tokens until it reaches a statement boundary (`;`, `int`, `float`, `print`, or `EOF`). The parser can then resume and detect further syntax errors in subsequent statements.

---

## Category 3: Abstract Syntax Trees (AST)

### Q11. What is the difference between a Parse Tree and an Abstract Syntax Tree (AST)?
**Answer:**  
- A **Parse Tree (Concrete Syntax Tree)** represents every syntactic derivation step in the formal grammar, including redundant parentheses, semicolons, and intermediate non-terminals.
- An **AST** is a condensed, semantically meaningful representation containing only the essential computational structure (e.g., operator nodes with operand child nodes), omitting formatting tokens like semicolons and parentheses.

### Q12. How is the AST represented and visualized in your project?
**Answer:**  
The AST is represented using strongly-typed Python dataclasses (`ProgramNode`, `DeclarationNode`, `BinaryOpNode`, etc.). In the web interface, it is visualized in two formats:
1. An indented, human-readable textual tree.
2. An interactive visual node-link diagram rendered via Graphviz (with a graceful fallback if Graphviz binaries are unavailable on the host OS).

---

## Category 4: Semantic Analysis & Symbol Tables

### Q13. What is a Symbol Table and what information does it store?
**Answer:**  
A Symbol Table is a compile-time data structure that tracks identifiers declared in the program. Each entry in our `SymbolTable` stores:
- Variable identifier name
- Declared data type (`int` or `float`)
- Source declaration line and column
- Initialization status (`is_initialized`)
- Line number of the most recent assignment

### Q14. What semantic checks does your application perform?
**Answer:**  
1. **Duplicate Declaration (`SEM001`):** Flags if an identifier is declared more than once in the same scope.
2. **Undeclared Variable Usage (`SEM002`):** Flags if a variable is used in an expression or assigned to without a prior declaration.
3. **Uninitialized Variable Warning (`SEM003`):** Warns if a variable is read before receiving a value.
4. **Static Division by Zero (`SEM004`):** Detects compile-time division by literal zero (`/ 0`).
5. **Type Narrowing Warning (`SEM005`):** Warns when assigning a floating-point expression to an integer variable due to precision loss.

---

## Category 5: Intermediate Code Generation (Three-Address Code)

### Q15. What is Three-Address Code (TAC)?
**Answer:**  
Three-Address Code is an intermediate representation (IR) where every instruction has at most one operator and at most three address references (two operands and one result), typically in the form `result = arg1 op arg2`.

### Q16. Why is Intermediate Code Generation useful?
**Answer:**  
IR decouples the compiler front-end (language-specific analysis) from the compiler back-end (machine-specific target code generation). This facilitates machine-independent optimizations (like constant folding, dead code elimination) and allows compiling $M$ source languages to $N$ machine targets with $M + N$ components instead of $M \times N$.

### Q17. How are temporary variables generated during expression translation?
**Answer:**  
Our `TACGenerator` maintains a counter that allocates sequential temporary variables (`t1`, `t2`, `t3`, ...). When translating a nested expression such as `int c = a + b * 2;`, it emits:
```
t1 = b * 2
t2 = a + t1
c = t2
```

---

## Category 6: Database & Software Architecture

### Q18. Why choose SQLite over other relational databases like MySQL or PostgreSQL?
**Answer:**  
SQLite is serverless, zero-configuration, ACID-compliant, and embedded directly inside Python via the standard `sqlite3` library. The entire database is stored in a single local file (`compiler.db`). It eliminates external setup requirements, making college demonstrations and offline faculty grading reliable.

### Q19. How is relational data integrity maintained in your SQLite schema?
**Answer:**  
We explicitly execute `PRAGMA foreign_keys = ON;` on every database connection. Tables `tokens`, `errors`, and `compilation_artifacts` have `FOREIGN KEY` constraints with `ON DELETE CASCADE` referencing `compilations(id)`. Deleting a compilation cleanly cascades to remove its dependent tokens, errors, and artifacts.

### Q20. What is stored in the `compilation_artifacts` table?
**Answer:**  
It stores serialized JSON representations of the generated Abstract Syntax Tree and the plain-text Three-Address Code output, allowing users to inspect past compilation artifacts without re-compiling.

---

## Category 7: Practical Demonstration Scenarios

### Q21. Show what happens when a semicolon is omitted.
**Answer / Action:**  
Load Sample 06. The analyzer highlights line 2 with error code `SYN001`: *"Expected ';' after declaration of 'a'"*, suggests adding `;`, and recovers to parse the remaining statements.

### Q22. Show what happens when a variable is used without declaration.
**Answer / Action:**  
Load Sample 10. Lexical and syntax phases succeed, but the semantic phase detects `SEM002`: *"Undeclared variable 'speed'"*, displaying the line and column number.

### Q23. Is arbitrary Python code executed when compiling user programs?
**Answer:**  
No. The application **never** uses `eval()` or `exec()`. User programs are strictly tokenized and parsed by our own custom lexer and recursive-descent parser, preventing code injection or security vulnerabilities.

