# Automated Test Suite Execution Results

**Date of Execution:** 2026-10-23  
**Environment:** Python 3.12.10 (win32)  
**Test Framework:** pytest-9.1.1  
**Total Tests:** 37  
**Passed:** 37  
**Failed:** 0  
**Execution Time:** 0.58 seconds  
**Pass Rate:** 100%

---

## 1. Test Execution Summary Table

| # | Test Name | Purpose | Expected Outcome | Actual Outcome | Status |
| :---: | :--- | :--- | :--- | :--- | :---: |
| 1 | `test_program_crud_operations` | Verify Program Creation, Read, Update, Search, and Delete in SQLite | Successful CRUD lifecycle with correct ID and values | All CRUD operations executed cleanly | **PASSED** |
| 2 | `test_record_successful_compilation` | Verify atomic storage of successful compilation run, tokens, and TAC | Compilation recorded with status `SUCCESS`, tokens, and artifacts | Row inserted, tokens stored, artifacts intact | **PASSED** |
| 3 | `test_record_failed_compilation` | Verify storage of failed compilation with diagnostic errors | Compilation recorded with status `FAILED` and error records | Recorded with error code `SYN001` | **PASSED** |
| 4 | `test_foreign_key_enforcement` | Confirm SQLite rejects orphan child records referencing non-existent runs | `sqlite3.IntegrityError` raised | IntegrityError raised as expected | **PASSED** |
| 5 | `test_dashboard_statistics` | Check live aggregate calculation of programs, runs, and pass rate | Accurate counts and calculated pass percentage | Exact numeric match (50.0% pass rate) | **PASSED** |
| 6 | `test_keywords_recognition` | Verify tokenization of `int`, `float`, and `print` keywords | Recognized as respective `TokenType.KEYWORD_*` | Correct enum classifications | **PASSED** |
| 7 | `test_keyword_vs_longer_identifier` | Ensure keyword `int` is not confused with identifiers like `integerValue` | `int` -> Keyword, `integerValue` -> Identifier | Disambiguated properly | **PASSED** |
| 8 | `test_integer_and_float_literals` | Validate parsing of integer and floating-point numeric constants | Numeric tokens generated with correctly typed Python values | Value and type conversions verified | **PASSED** |
| 9 | `test_operators_and_delimiters` | Verify tokenization of `=`, `+`, `-`, `*`, `/`, `;`, `(`, `)` | Recognized as distinct operator and separator tokens | Exact token sequence matched | **PASSED** |
| 10 | `test_line_and_column_tracking` | Ensure 1-based line and column coordinates match character offsets | Correct (line, column) tuples across multiple lines | Accurate spatial tracking | **PASSED** |
| 11 | `test_comments_and_whitespace_ignored` | Confirm single-line comments `//` and spaces are skipped | Comments stripped without disturbing line tracking | Only program tokens returned | **PASSED** |
| 12 | `test_unrecognized_characters_detection`| Test detection of invalid symbols (`@`, `#`, `$`) | Scanner logs `LEX001` errors and marks tokens `UNKNOWN` | 3 `LEX001` diagnostics logged | **PASSED** |
| 13 | `test_malformed_numeric_literal` | Test detection of numbers with multiple decimal points (`12.34.56`) | Scanner logs `LEX002` diagnostic | `LEX002` error registered | **PASSED** |
| 14 | `test_invalid_identifier_starting_with_digit` | Test detection of identifiers starting with digits (`99bottles`) | Scanner logs `LEX003` diagnostic | `LEX003` error registered | **PASSED** |
| 15 | `test_valid_declarations` | Verify parsing of valid `int` and `float` variable declarations | `DeclarationNode` instances created in AST | Nodes created with correct attributes | **PASSED** |
| 16 | `test_valid_assignment_and_print` | Verify parsing of assignment statements and `print(...)` statements | AST populated with `AssignmentNode` and `PrintStatementNode` | AST constructed without errors | **PASSED** |
| 17 | `test_operator_precedence` | Verify that `*` binds tighter than `+` in `a + b * 2` | Root node is `+`, right child is binary `*` | Tree hierarchy enforces precedence | **PASSED** |
| 18 | `test_parentheses_override_precedence` | Verify that `(a + b) * 2` forces addition before multiplication | Root node is `*`, left child is binary `+` | Tree hierarchy enforces parentheses | **PASSED** |
| 19 | `test_missing_semicolon` | Test error detection when statement omits trailing `;` | Parser logs `SYN001` error and continues parsing | `SYN001` diagnostic logged | **PASSED** |
| 20 | `test_unmatched_parenthesis` | Test error detection for missing closing parenthesis `)` | Parser logs `SYN002` error referencing opening coordinate | `SYN002` diagnostic logged | **PASSED** |
| 21 | `test_missing_identifier_in_declaration`| Detect missing variable name in declaration (`int = 10;`) | Parser logs `SYN003` error | `SYN003` diagnostic logged | **PASSED** |
| 22 | `test_missing_equals_in_declaration` | Detect missing assignment operator in declaration (`int a 10;`) | Parser logs `SYN004` error | `SYN004` diagnostic logged | **PASSED** |
| 23 | `test_unexpected_token_in_expression` | Detect syntax error when expression contains illegal token (`a = + ;`) | Parser logs `SYN005` error | `SYN005` diagnostic logged | **PASSED** |
| 24 | `test_empty_input` | Ensure parser handles blank or whitespace-only code gracefully | Empty `ProgramNode` with 0 statements, no crashes | ProgramNode with 0 statements | **PASSED** |
| 25 | `test_pipeline_valid_program` | Test end-to-end compilation of multi-statement valid program | Status `SUCCESS`, AST, Symbol Table, and TAC populated | All artifacts produced | **PASSED** |
| 26 | `test_pipeline_lexical_failure` | Test pipeline halt/diagnostic handling on lexical errors | Status `FAILED`, error count > 0 | Correctly marked as FAILED | **PASSED** |
| 27 | `test_pipeline_syntax_failure` | Test pipeline diagnostic handling on syntax errors | Status `FAILED`, syntax error reported | Correctly marked as FAILED | **PASSED** |
| 28 | `test_pipeline_semantic_failure` | Test pipeline diagnostic handling on semantic errors | Status `FAILED`, semantic error reported | Correctly marked as FAILED | **PASSED** |
| 29 | `test_symbol_table_population` | Verify symbol table correctly records variable names and types | Symbols for `a` (int) and `b` (float) registered | Correctly registered | **PASSED** |
| 30 | `test_duplicate_declaration` | Test semantic detection of redeclaring variable in same scope | Diagnostic `SEM001` logged | `SEM001` diagnostic logged | **PASSED** |
| 31 | `test_undeclared_variable_in_assignment` | Test semantic detection of assigning to undeclared identifier | Diagnostic `SEM002` logged | `SEM002` diagnostic logged | **PASSED** |
| 32 | `test_undeclared_variable_in_expression` | Test semantic detection of reading undeclared identifier | Diagnostic `SEM002` logged | `SEM002` diagnostic logged | **PASSED** |
| 33 | `test_static_division_by_zero` | Test compile-time detection of division by literal zero | Diagnostic `SEM004` logged | `SEM004` diagnostic logged | **PASSED** |
| 34 | `test_tac_simple_declaration` | Verify TAC emission for `int a = 10;` | Emits `a = 10` | Generated `a = 10` | **PASSED** |
| 35 | `test_tac_expression_precedence` | Verify TAC emission preserving precedence in `a + b * 2` | Emits `t1 = b * 2`, `t2 = a + t1`, `c = t2` | Exact 3AC sequence verified | **PASSED** |
| 36 | `test_tac_parenthesized_expression` | Verify TAC emission preserving grouping in `(a + b) * 2` | Emits `t1 = a + b`, `t2 = t1 * 2`, `c = t2` | Exact 3AC sequence verified | **PASSED** |
| 37 | `test_tac_print_statement` | Verify TAC emission for `print(x * 5);` | Emits `t1 = x * 5`, `print t1` | Exact 3AC sequence verified | **PASSED** |

---

## 2. Conclusion
All 37 unit and integration tests passed reliably with zero errors and zero warnings, confirming complete adherence to the project specifications.

