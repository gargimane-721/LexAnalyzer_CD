"""
Generates the official college project report in editable Microsoft Word (.docx) format.
Designed according to the engineering report formatting standards of:
Shri Sant Gajanan Maharaj College of Engineering, Shegaon.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def set_cell_background(cell, color_hex):
    """Sets background shading of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)


def create_report():
    doc = Document()

    # Set 1-inch margins throughout the document
    sections = doc.sections
    for s in sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    # -------------------------------------------------------------
    # STYLES CONFIGURATION
    # -------------------------------------------------------------
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.line_spacing = 1.25
    normal_style.paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # 1. COVER PAGE
    # -------------------------------------------------------------
    p_pre = doc.add_paragraph()
    p_pre.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_pre = p_pre.add_run("A TECHNICAL ENHANCEMENT COURSE (TEC) MINI-PROJECT REPORT ON\n")
    r_pre.bold = True
    r_pre.font.size = Pt(13)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("SMART LEXICAL ANALYZER AND SYNTAX CHECKER USING PYTHON\n")
    r_title.bold = True
    r_title.font.size = Pt(18)
    r_title.font.color.rgb = RGBColor(30, 58, 138)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run(
        "Submitted in Partial Fulfillment of the Requirements for the Degree of\n"
        "BACHELOR OF ENGINEERING\n"
        "IN\n"
        "COMPUTER SCIENCE AND ENGINEERING\n"
    )
    r_sub.bold = True
    r_sub.font.size = Pt(12)

    p_course = doc.add_paragraph()
    p_course.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_course = p_course.add_run(
        "Subject: Compiler Design — TEC Assignment (Course Code: 5CS221PC)\n"
        "Academic Year: Third Year, Fifth Semester (Session: 2026–2027)\n"
    )
    r_course.font.size = Pt(11)
    r_course.italic = True

    doc.add_paragraph("\n")

    p_by = doc.add_paragraph()
    p_by.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_by = p_by.add_run("SUBMITTED BY:\n")
    r_by.bold = True
    r_by.font.size = Pt(12)

    students_table = doc.add_table(rows=1, cols=3)
    students_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = students_table.rows[0].cells
    hdr[0].paragraphs[0].add_run("Roll No.").bold = True
    hdr[1].paragraphs[0].add_run("Student Full Name").bold = True
    hdr[2].paragraphs[0].add_run("Degree & Year").bold = True

    demo_students = [
        ("5CS01", "Student Name 1", "B.E. CSE — Third Year"),
        ("5CS02", "Student Name 2", "B.E. CSE — Third Year"),
        ("5CS03", "Student Name 3", "B.E. CSE — Third Year"),
    ]
    for roll, name, deg in demo_students:
        row = students_table.add_row().cells
        row[0].paragraphs[0].add_run(roll)
        row[1].paragraphs[0].add_run(name)
        row[2].paragraphs[0].add_run(deg)

    doc.add_paragraph("\n")

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run(
        "DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\n"
        "SHRI SANT GAJANAN MAHARAJ COLLEGE OF ENGINEERING, SHEGAON\n"
        "(Approved by AICTE, New Delhi & Affiliated to Sant Gadge Baba Amravati University)\n"
        "Shegaon – 444503, District Buldhana, Maharashtra, India\n"
        "Autumn/Winter Session: 2026–2027"
    )
    r_inst.bold = True
    r_inst.font.size = Pt(11)

    doc.add_page_break()

    # -------------------------------------------------------------
    # 2. CERTIFICATE OF APPROVAL
    # -------------------------------------------------------------
    h_cert = doc.add_heading("CERTIFICATE OF APPROVAL", level=1)
    h_cert.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_cert = doc.add_paragraph(
        "This is to certify that the Technical Enhancement Course (TEC) mini-project report entitled "
        "'Smart Lexical Analyzer and Syntax Checker Using Python' is a bonafide work carried out by "
        "the following students of Third Year B.E. Computer Science and Engineering at Shri Sant Gajanan "
        "Maharaj College of Engineering, Shegaon, during the academic year 2026–2027:"
    )
    p_cert.paragraph_format.line_spacing = 1.3

    cert_table = doc.add_table(rows=1, cols=3)
    cert_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    chdr = cert_table.rows[0].cells
    chdr[0].paragraphs[0].add_run("Roll No.").bold = True
    chdr[1].paragraphs[0].add_run("Candidate Name").bold = True
    chdr[2].paragraphs[0].add_run("Signature").bold = True

    for roll, name, _ in demo_students:
        crow = cert_table.add_row().cells
        crow[0].paragraphs[0].add_run(roll)
        crow[1].paragraphs[0].add_run(name)
        crow[2].paragraphs[0].add_run("_________________")

    doc.add_paragraph("\n")
    p_cert2 = doc.add_paragraph(
        "This report is approved as meeting the required standards of the course Compiler Design (5CS221PC) "
        "for the degree of Bachelor of Engineering in Computer Science and Engineering."
    )
    p_cert2.paragraph_format.line_spacing = 1.3

    doc.add_paragraph("\n\n")

    sig_table = doc.add_table(rows=1, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    scells = sig_table.rows[0].cells
    scells[0].paragraphs[0].add_run(
        "_____________________________\n"
        "Project Guide / Course In-Charge\n"
        "Department of CSE\n"
        "SSGMCE, Shegaon"
    ).bold = True
    scells[1].paragraphs[0].add_run(
        "_____________________________\n"
        "Head of the Department (CSE)\n"
        "Department of CSE\n"
        "SSGMCE, Shegaon"
    ).bold = True
    scells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_page_break()

    # -------------------------------------------------------------
    # 3. DECLARATION & ACKNOWLEDGEMENTS
    # -------------------------------------------------------------
    h_dec = doc.add_heading("CANDIDATE DECLARATION", level=1)
    h_dec.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph(
        "We hereby declare that this TEC mini-project report entitled 'Smart Lexical Analyzer and "
        "Syntax Checker Using Python' represents our original work completed under the academic supervision "
        "of the Department of Computer Science & Engineering, Shri Sant Gajanan Maharaj College of Engineering, Shegaon.\n\n"
        "We have adhered to all academic integrity principles. All external literature, documentation, and references "
        "have been properly cited. This report has not been submitted previously to any university or examining body for the "
        "award of any other degree or diploma."
    )
    doc.add_paragraph("\nDate: 23 October 2026\nPlace: Shegaon, Maharashtra\n\nSignatures of the Candidates:")
    doc.add_paragraph("1. ________________________     2. ________________________     3. ________________________")

    doc.add_paragraph("\n")
    h_ack = doc.add_heading("ACKNOWLEDGEMENTS", level=1)
    h_ack.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph(
        "We wish to express our deep sense of gratitude to Shri Sant Gajanan Maharaj College of Engineering (SSGMCE), "
        "Shegaon, for providing excellent laboratory and computing facilities to execute our Compiler Design project.\n\n"
        "We are profoundly indebted to our Course In-Charge and Faculty Guide for invaluable technical guidance, constructive "
        "reviews, and constant encouragement during the development of our lexer, recursive-descent parser, symbol table manager, "
        "and Streamlit interface.\n\n"
        "We also convey our sincere thanks to the Head of the Computer Science & Engineering Department and all faculty members "
        "for their continuous academic support."
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # 4. ABSTRACT
    # -------------------------------------------------------------
    h_abs = doc.add_heading("ABSTRACT", level=1)
    h_abs.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph(
        "In modern computer science education, Compiler Design provides students with essential insights into program analysis, "
        "formal grammars, and language processing. Traditional teaching approaches often utilize archaic command-line tools like "
        "Lex and Yacc, which provide cryptic error diagnostics and lack visual interactive inspection.\n\n"
        "This Technical Enhancement Course (TEC) project introduces 'Smart Lexical Analyzer and Syntax Checker Using Python', "
        "a complete, web-based educational workbench developed in Python 3.12 and Streamlit, coupled with a local SQLite relational "
        "database. The application supports a deterministic subset of C-like syntax comprising integer and float declarations, variable "
        "assignments, algebraic expressions enforcing arithmetic operator precedence, parentheses grouping, single-line comments, "
        "and formatted print statements.\n\n"
        "The compiler architecture incorporates four cleanly decoupled analytical phases:\n"
        "1. Lexical Analysis (Scanner): Identifies keywords, identifiers, literals, operators, and separators with 1-based line/column tracking.\n"
        "2. Syntax Analysis (Parser): Implements a hand-crafted recursive-descent parser with panic-mode error recovery, constructing an Abstract Syntax Tree (AST).\n"
        "3. Semantic Analysis: Maintains an active Symbol Table verifying variable scope, detecting duplicate declarations, checking for undeclared identifiers, and detecting static compile-time division by zero.\n"
        "4. Intermediate Code Generation: Linearizes expressions into Three-Address Code (TAC) with sequential temporary registers.\n\n"
        "The application automatically records all programs, compilation runs, token streams, diagnostic errors, and serialized artifacts "
        "into SQLite ('compiler.db') with strict foreign-key enforcement. An automated suite of 37 pytest tests achieves a 100% pass rate. "
        "The platform provides an ideal demonstrative tool for viva examinations and foundational compiler education."
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTERS 1 - 8
    # -------------------------------------------------------------
    chapters = [
        ("CHAPTER 1: INTRODUCTION", [
            ("1.1 Background & Motivation",
             "Compiler construction connects theoretical computing concepts (automata, grammars) with practical software implementation. "
             "Traditional laboratory curricula heavily rely on legacy Unix tools that present steep learning curves, minimal interactivity, "
             "and opaque diagnostic messages. Building an educational compiler with an interactive browser interface allows students to inspect "
             "every internal transformation step-by-step."),
            ("1.2 Problem Statement",
             "Undergraduate students require an educational compiler platform capable of accepting C-like programs, breaking them into classified "
             "tokens with line/column coordinates, checking syntax against formal grammar, building Abstract Syntax Trees, checking variable scopes, "
             "generating Three-Address Code, and recording history in a relational database."),
            ("1.3 Project Objectives",
             "The primary goals are: (1) Define an unambiguous C-like grammar in EBNF; (2) Implement a regular-expression-based scanner with 1-based tracking; "
             "(3) Implement a top-down recursive-descent parser with error synchronization; (4) Implement semantic symbol table checking; (5) Generate Three-Address Code; "
             "(6) Persist programs and compilations in SQLite; (7) Build an interactive Streamlit UI; (8) Achieve 100% automated test coverage with pytest."),
            ("1.4 Scope and Educational Focus",
             "The project emphasizes clarity, pedagogical value, and reliable demonstration rather than attempting to reproduce a complete industrial C compiler. "
             "All phases are modularized and thoroughly documented for college viva defense."),
            ("1.5 Limitations",
             "The system intentionally excludes pointers, preprocessor directives, structs, arrays, and custom functions. Arbitrary code execution (eval/exec) "
             "is strictly forbidden.")
        ]),

        ("CHAPTER 2: THEORETICAL FOUNDATIONS & LITERATURE SURVEY", [
            ("2.1 The Traditional Compiler Pipeline",
             "Classical compilers divide compilation into front-end analysis (Lexical, Syntax, Semantic Analysis) and back-end synthesis "
             "(Intermediate Code Generation, Optimization, Target Code Generation). This project provides complete visibility into front-end analysis and intermediate code emission."),
            ("2.2 Lexical Analysis & Regular Grammars",
             "The scanner groups input characters into lexemes and classifies them into tokens using regular expressions. Unknown characters emit diagnostic records without crashing."),
            ("2.3 Syntax Analysis & Recursive-Descent Parsing",
             "Context-Free Grammars (CFGs) define structural validity. Top-down recursive-descent parsing maps non-terminals to dedicated functions. Grammars must be free of left-recursion."),
            ("2.4 Panic-Mode Error Synchronization",
             "When a syntax error occurs, the parser logs the diagnostic and synchronizes by advancing until a statement terminator (semicolon or keyword) is found, allowing multiple syntax errors to be detected in one pass."),
            ("2.5 Intermediate Code (Three-Address Code)",
             "Three-Address Code (TAC) linearizes nested tree structures into instructions with at most one operator and three addresses (result = arg1 op arg2), preparing expressions for execution and optimization.")
        ]),

        ("CHAPTER 3: SYSTEM REQUIREMENTS & SPECIFICATIONS", [
            ("3.1 Hardware Specifications",
             "Standard dual-core x86_64 or ARM processor, 4 GB RAM (8 GB recommended), 100 MB free disk space, minimum 1280x720 display resolution."),
            ("3.2 Software Environment",
             "Windows 10/11 (PowerShell/CMD), Linux, or macOS. Python 3.11 or 3.12. Modern web browser (Chrome, Firefox, Edge)."),
            ("3.3 Technology Stack",
             "Python 3.12 (core programming), Streamlit (web GUI), SQLite3 (persistent ACID database), Pandas (data table formatting), pytest (automated testing), Graphviz (AST visualization), python-docx (report generation).")
        ]),

        ("CHAPTER 4: SYSTEM ARCHITECTURE & DESIGN", [
            ("4.1 High-Level Architecture",
             "A sequential, decoupled pipeline: Source Code -> Lexer -> Parser -> Semantic Analyzer -> TAC Generator -> Diagnostics -> SQLite Database & Streamlit GUI."),
            ("4.2 Formal Source Grammar (EBNF)",
             "program = { statement } , EOF ;\n"
             "statement = declaration | assignment | print_statement ;\n"
             "declaration = TYPE , IDENTIFIER , '=' , expression , ';' ;\n"
             "assignment = IDENTIFIER , '=' , expression , ';' ;\n"
             "print_statement = 'print' , '(' , expression , ')' , ';' ;\n"
             "expression = term , { ('+' | '-') , term } ;\n"
             "term = factor , { ('*' | '/') , factor } ;\n"
             "factor = NUMBER | IDENTIFIER | '(' , expression , ')' | unary_expression ;\n"
             "unary_expression = ('+' | '-') , factor ;\n"
             "TYPE = 'int' | 'float' ;\n"
             "NUMBER = INT_LITERAL | FLOAT_LITERAL ;"),
            ("4.3 Operator Precedence & Associativity",
             "1. Parentheses () (highest)\n2. Unary (+, -)\n3. Multiplicative (*, /)\n4. Additive (+, -)\n5. Assignment (=) (lowest)."),
            ("4.4 Relational Database Design",
             "Tables: 'programs' (saved source scripts), 'compilations' (immutable run snapshots), 'tokens' (individual tokens), 'errors' (diagnostics), 'compilation_artifacts' (AST JSON & TAC text). Foreign keys enforced with PRAGMA foreign_keys = ON.")
        ]),

        ("CHAPTER 5: IMPLEMENTATION DETAILS", [
            ("5.1 Lexical Analyzer Module (compiler/lexer.py)",
             "Uses pre-compiled master regular expressions. Identifies keywords, identifiers, literals, operators, delimiters. Discards comments and whitespace while updating 1-based line and column offsets."),
            ("5.2 AST Node Structure (compiler/ast_nodes.py)",
             "Strongly-typed dataclasses: ProgramNode, DeclarationNode, AssignmentNode, PrintStatementNode, BinaryOpNode, UnaryOpNode, NumberLiteralNode, VariableNode."),
            ("5.3 Recursive-Descent Parser (compiler/parser.py)",
             "Implements statement parsing, expression evaluation respecting precedence, semicolon verification, and panic-mode error recovery."),
            ("5.4 Semantic Analyzer (compiler/semantic.py)",
             "Maintains SymbolTable tracking variable names, types, declaration coordinates, and initialization state. Detects duplicate declarations, undeclared variables, and static division by zero."),
            ("5.5 Intermediate Code Generator (compiler/tac.py)",
             "Translates expressions into TAC instructions with temporary variables (t1, t2, ...). Emits only when preceding phases pass."),
            ("5.6 SQLite Repository Layer (database/repository.py)",
             "Provides clean parameterized SQL queries, atomic transactions, history logging, and dashboard metric calculations."),
            ("5.7 Streamlit Web Application (app.py)",
             "Provides 7 sections: Dashboard, Code Analyzer, Token Analysis, Error Report, Saved Programs, Compilation History, About & Help.")
        ]),

        ("CHAPTER 6: SOFTWARE TESTING & QUALITY ASSURANCE", [
            ("6.1 Testing Methodology",
             "Structured testing using pytest: unit tests for each compiler module, integration tests for full pipeline, negative tests for malformed inputs, and database integrity tests."),
            ("6.2 Automated Test Suite Results (37 Tests)",
             "37 tests executed in 0.58s with a 100% pass rate. Covers keywords, identifiers, numeric literals, comments, error diagnostics, operator precedence, symbol table checks, TAC generation, and SQLite foreign-key enforcement."),
            ("6.3 Security Safeguards",
             "Strictly avoids eval() or exec(). Source code is parsed only by our custom lexer and recursive-descent parser, eliminating code execution vulnerabilities.")
        ]),

        ("CHAPTER 7: RESULTS & DEMONSTRATION WALKTHROUGH", [
            ("7.1 Real-Time Analytics Dashboard",
             "Displays total saved programs, total compilation attempts, passed runs, failed runs, success percentage, and recent activity log from SQLite."),
            ("7.2 Code Analyzer Demonstration",
             "Demonstrates successful compilation of sample programs: token stream display, textual/visual AST representation, populated symbol table, and generated TAC."),
            ("7.3 Diagnostic Error Handling",
             "Demonstrates detection of missing semicolons (SYN001), unmatched parentheses (SYN002), undeclared variables (SEM002), and illegal characters (LEX001) with actionable suggestions.")
        ]),

        ("CHAPTER 8: CONCLUSION & FUTURE SCOPE", [
            ("8.1 Summary of Contributions",
             "Successfully developed and verified a complete, educational, web-based Compiler Design application in Python and Streamlit with SQLite persistence, 100% test coverage, and transparent viva inspection."),
            ("8.2 Future Scope",
             "Future extensions include control flow statements (if-else, while, for loops), constant folding optimizations, virtual stack machine code generation, and multi-scope symbol tables.")
        ])
    ]

    for ch_title, sections in chapters:
        h_ch = doc.add_heading(ch_title, level=1)
        h_ch.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for sec_title, sec_text in sections:
            doc.add_heading(sec_title, level=2)
            doc.add_paragraph(sec_text)
        doc.add_page_break()

    # -------------------------------------------------------------
    # REFERENCES
    # -------------------------------------------------------------
    doc.add_heading("REFERENCES", level=1)
    refs = [
        "Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). Compilers: Principles, Techniques, and Tools (2nd ed.). Addison-Wesley.",
        "Cooper, K. D., & Torczon, L. (2011). Engineering a Compiler (2nd ed.). Morgan Kaufmann.",
        "Louden, K. C. (1997). Compiler Construction: Principles and Practice. PWS Publishing Company.",
        "Grune, D., Bal, H. E., Jacobs, C. J., & Langendoen, K. G. (2012). Modern Compiler Design (2nd ed.). Springer.",
        "Python Software Foundation. (2026). Python 3.12 Documentation: 're' and 'sqlite3' Modules. https://docs.python.org/3/",
        "Streamlit Inc. (2026). Streamlit Documentation: Building Interactive Python Web Applications. https://docs.streamlit.io/"
    ]
    for r in refs:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.5)
        p.add_run(r)

    doc.add_page_break()

    # -------------------------------------------------------------
    # APPENDIX: VIVA VOCE DEFENSE GUIDE
    # -------------------------------------------------------------
    doc.add_heading("APPENDIX: VIVA VOCE DEFENSE GUIDE", level=1)
    viva_samples = [
        ("Q1: What is the primary role of the Lexical Analyzer (Scanner)?",
         "The scanner breaks source code characters into classified tokens (keywords, identifiers, literals, operators, separators), removes comments and whitespace, and tracks line and column coordinates."),
        ("Q2: Why use a Recursive-Descent Parser for this project?",
         "It maps grammar rules directly to Python methods, making it clean, easy to debug, free of external build steps, and straightforward to explain during viva."),
        ("Q3: How does the parser handle operator precedence?",
         "Precedence is enforced structurally in the grammar: primary factors (parentheses, literals) bind tightest, followed by multiplicative terms, followed by additive expressions."),
        ("Q4: What is Three-Address Code (TAC)?",
         "An intermediate representation where each instruction has at most one operator and three addresses (result = arg1 op arg2), breaking complex expressions into sequential operations with temporary variables."),
        ("Q5: How does the application guarantee relational data integrity?",
         "By executing 'PRAGMA foreign_keys = ON;' on every SQLite connection and establishing cascading foreign keys from tokens, errors, and artifacts to compilation records.")
    ]
    for q, a in viva_samples:
        p_q = doc.add_paragraph()
        p_q.add_run(q).bold = True
        doc.add_paragraph(a)

    # Save to docs/TEC_Project_Report.docx
    output_path = os.path.join(os.path.dirname(__file__), "TEC_Project_Report.docx")
    doc.save(output_path)
    print(f"Report generated successfully: {output_path}")


if __name__ == "__main__":
    create_report()

