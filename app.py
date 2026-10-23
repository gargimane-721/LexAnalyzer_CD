"""
Smart Lexical Analyzer & Syntax Checker
Web-based educational Compiler Design platform built with Streamlit and SQLite.
Subject: Compiler Design — TEC Assignment (5CS221PC)
College: Shri Sant Gajanan Maharaj College of Engineering, Shegaon
"""

import json
import os
import streamlit as st
import pandas as pd
from typing import Optional

from compiler.pipeline import compile_source
from compiler.diagnostics import CompilationResult, DiagnosticPhase
from database.db import DatabaseManager, db_manager
from database.repository import CompilerRepository

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Smart Lexical Analyzer & Syntax Checker",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Repository
repo = CompilerRepository(db_manager)

# Load Sample Programs
SAMPLES_FILE = os.path.join(os.path.dirname(__file__), "samples", "sample_programs.json")
samples_data = []
if os.path.exists(SAMPLES_FILE):
    try:
        with open(SAMPLES_FILE, "r", encoding="utf-8") as f:
            samples_data = json.load(f)
    except Exception:
        samples_data = []

# Initialize Session State
if "source_code" not in st.session_state:
    st.session_state["source_code"] = (
        "// Welcome to Smart Lexical Analyzer & Syntax Checker!\n"
        "// Enter C-like statements below or select a sample program.\n\n"
        "int a = 10;\n"
        "float b = 5.5;\n"
        "int c = (a + 5) * 2;\n"
        "print(c);"
    )
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None
if "current_program_name" not in st.session_state:
    st.session_state["current_program_name"] = "Untitled Program"
if "current_program_id" not in st.session_state:
    st.session_state["current_program_id"] = None


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def render_ast_text(node, indent=0) -> str:
    """Recursively formats an AST node into an indented hierarchical string."""
    if not node:
        return "None"
    prefix = "  " * indent
    node_type = type(node).__name__

    if node_type == "ProgramNode":
        lines = [f"{prefix}ProgramNode:"]
        for stmt in node.statements:
            lines.append(render_ast_text(stmt, indent + 1))
        return "\n".join(lines)

    elif node_type == "DeclarationNode":
        return f"{prefix}DeclarationNode: {node.var_type} {node.identifier}\n{prefix}  Expression:\n{render_ast_text(node.expression, indent + 2)}"

    elif node_type == "AssignmentNode":
        return f"{prefix}AssignmentNode: {node.identifier} =\n{render_ast_text(node.expression, indent + 1)}"

    elif node_type == "PrintStatementNode":
        return f"{prefix}PrintStatementNode:\n{render_ast_text(node.expression, indent + 1)}"

    elif node_type == "BinaryOpNode":
        return (
            f"{prefix}BinaryOpNode: (Operator: '{node.operator}')\n"
            f"{prefix}  Left:\n{render_ast_text(node.left, indent + 2)}\n"
            f"{prefix}  Right:\n{render_ast_text(node.right, indent + 2)}"
        )

    elif node_type == "UnaryOpNode":
        return f"{prefix}UnaryOpNode: '{node.operator}'\n{render_ast_text(node.operand, indent + 1)}"

    elif node_type == "NumberLiteralNode":
        return f"{prefix}NumberLiteralNode: {node.value} ({node.num_type})"

    elif node_type == "VariableNode":
        return f"{prefix}VariableNode: {node.name}"

    return f"{prefix}{node_type}"


def render_ast_graphviz(node):
    """Generates a Graphviz Digraph for visual AST rendering if graphviz is available."""
    try:
        import graphviz
        dot = graphviz.Digraph(comment="Abstract Syntax Tree")
        dot.attr("node", shape="box", style="rounded,filled", fillcolor="#1E293B", fontcolor="#F8FAFC", fontname="Courier")
        dot.attr("edge", color="#64748B")

        counter = [0]

        def add_node(n):
            counter[0] += 1
            node_id = f"node_{counter[0]}"
            tname = type(n).__name__

            if tname == "ProgramNode":
                dot.node(node_id, "Program", fillcolor="#2563EB")
                for s in n.statements:
                    sid = add_node(s)
                    dot.edge(node_id, sid)

            elif tname == "DeclarationNode":
                label = f"Decl: {n.var_type} {n.identifier}"
                dot.node(node_id, label, fillcolor="#0D9488")
                eid = add_node(n.expression)
                dot.edge(node_id, eid, label="init")

            elif tname == "AssignmentNode":
                label = f"Assign: {n.identifier}"
                dot.node(node_id, label, fillcolor="#D97706")
                eid = add_node(n.expression)
                dot.edge(node_id, eid, label="val")

            elif tname == "PrintStatementNode":
                dot.node(node_id, "PrintStmt", fillcolor="#9333EA")
                eid = add_node(n.expression)
                dot.edge(node_id, eid)

            elif tname == "BinaryOpNode":
                dot.node(node_id, f"Op: {n.operator}", fillcolor="#3B82F6")
                lid = add_node(n.left)
                rid = add_node(n.right)
                dot.edge(node_id, lid, label="L")
                dot.edge(node_id, rid, label="R")

            elif tname == "UnaryOpNode":
                dot.node(node_id, f"Unary: {n.operator}", fillcolor="#3B82F6")
                oid = add_node(n.operand)
                dot.edge(node_id, oid)

            elif tname == "NumberLiteralNode":
                dot.node(node_id, f"{n.value}\n({n.num_type})", fillcolor="#059669")

            elif tname == "VariableNode":
                dot.node(node_id, f"Var: {n.name}", fillcolor="#D97706")

            else:
                dot.node(node_id, str(tname))

            return node_id

        add_node(node)
        return dot
    except Exception:
        return None


# -----------------------------------------------------------------------------
# Sidebar Navigation & Branding
# -----------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### ⚡ Compiler Studio")
    st.caption("SSGMCE Shegaon • Autumn 2026–2027")
    st.caption("**Subject:** 5CS221PC — Compiler Design TEC")

    st.markdown("---")

    menu_option = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "💻 Code Analyzer",
            "🔍 Token Analysis",
            "⚠️ Error Report",
            "📁 Saved Programs",
            "📜 Compilation History",
            "ℹ️ About & Help"
        ],
        index=1
    )

    st.markdown("---")

    # Quick Live Stats in Sidebar
    try:
        quick_stats = repo.get_dashboard_statistics()
        st.markdown("#### 📈 Quick Stats")
        col1, col2 = st.columns(2)
        col1.metric("Programs", quick_stats["total_programs"])
        col2.metric("Pass Rate", f"{quick_stats['success_rate']}%")
        st.caption(f"Total Runs: {quick_stats['total_compilations']}")
    except Exception:
        pass

    st.markdown("---")
    st.markdown(
        "<small style='color: #94A3B8;'>Developed for Third Year B.E. CSE<br>"
        "Department of Computer Science & Engineering</small>",
        unsafe_allow_html=True
    )


# -----------------------------------------------------------------------------
# SECTION A: DASHBOARD
# -----------------------------------------------------------------------------

if menu_option == "📊 Dashboard":
    st.title("📊 Compiler Analytics Dashboard")
    st.markdown("Real-time telemetry and compilation metrics from the local SQLite database.")

    stats = repo.get_dashboard_statistics()

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("📁 Saved Programs", stats["total_programs"])
    m2.metric("🔄 Total Runs", stats["total_compilations"])
    m3.metric("✅ Passed", stats["successful_compilations"])
    m4.metric("❌ Failed", stats["failed_compilations"])
    m5.metric("📈 Success Rate", f"{stats['success_rate']}%")

    st.markdown("---")

    col_recent, col_info = st.columns([3, 2])

    with col_recent:
        st.subheader("🕒 Recent Compilation Activity")
        recent_history = repo.get_recent_compilations(limit=10)
        if recent_history:
            history_df = pd.DataFrame(recent_history)
            display_df = history_df[["id", "program_name_snapshot", "status", "token_count", "error_count", "duration_ms", "started_at"]].copy()
            display_df.columns = ["Run ID", "Program Name", "Status", "Tokens", "Errors", "Duration (ms)", "Timestamp"]
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("No compilation history found yet. Head to the **Code Analyzer** to compile your first program!")

    with col_info:
        st.subheader("💡 Compiler Pipeline Architecture")
        st.markdown(
            """
            The educational compiler executes in 4 strictly decoupled phases:
            1. **Lexical Analysis (Scanner):** Converts source text into categorized tokens with row/column coordinates.
            2. **Syntax Analysis (Parser):** Validates grammar using recursive descent and constructs the AST.
            3. **Semantic Analysis:** Symbol table registration, duplicate/undeclared variable checks, static zero-division detection.
            4. **Intermediate Code Generation:** Generates Three-Address Code (TAC) with temporary variables.
            """
        )


# -----------------------------------------------------------------------------
# SECTION B: CODE ANALYZER
# -----------------------------------------------------------------------------

elif menu_option == "💻 Code Analyzer":
    st.title("💻 Smart Lexical Analyzer & Syntax Checker")
    st.caption("Interactive development environment for writing, scanning, parsing, and inspecting C-like programs.")

    # Control bar for sample selection
    col_preset, col_load_btn, col_clear_btn = st.columns([4, 1, 1])

    sample_names = [f"{s['name']} ({s['expected_validity']})" for s in samples_data]

    with col_preset:
        selected_sample_idx = st.selectbox(
            "Load Sample Program Preset:",
            range(len(sample_names)),
            format_func=lambda idx: sample_names[idx] if samples_data else "No samples",
            index=0
        )

    with col_load_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("📥 Load Sample", use_container_width=True):
            if samples_data:
                sample_item = samples_data[selected_sample_idx]
                st.session_state["source_code"] = sample_item["source_code"]
                st.session_state["current_program_name"] = sample_item["name"]
                st.rerun()

    with col_clear_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🗑 Clear", use_container_width=True):
            st.session_state["source_code"] = ""
            st.session_state["last_result"] = None
            st.rerun()

    # Code Editor Input
    source_code_input = st.text_area(
        "Source Code Editor (C-like subset):",
        value=st.session_state.get("source_code", ""),
        height=220,
        placeholder="Enter your C-like statements here...",
        key="editor_text_area"
    )
    # Keep session state in sync
    st.session_state["source_code"] = source_code_input

    # Action Toolbar
    col_run, col_save, col_name = st.columns([1.5, 1.5, 3])

    with col_run:
        run_compile = st.button("▶ Run Analysis / Compile", type="primary", use_container_width=True)

    with col_save:
        save_clicked = st.button("💾 Save Program", use_container_width=True)

    with col_name:
        prog_name_input = st.text_input(
            "Program Label",
            value=st.session_state.get("current_program_name", "My C Script"),
            label_visibility="collapsed"
        )
        st.session_state["current_program_name"] = prog_name_input

    # Save Logic
    if save_clicked:
        if not source_code_input.strip():
            st.warning("Cannot save empty program source code.")
        else:
            new_id = repo.create_program(prog_name_input, source_code_input)
            st.session_state["current_program_id"] = new_id
            st.success(f"Program '{prog_name_input}' saved successfully with ID #{new_id}!")

    # Compilation Execution Logic
    if run_compile:
        if not source_code_input.strip():
            st.warning("Please provide source code before running compilation.")
        else:
            result = compile_source(source_code_input)
            st.session_state["last_result"] = result

            # Record into SQLite compilation history
            try:
                comp_id = repo.record_compilation(
                    result,
                    program_id=st.session_state.get("current_program_id"),
                    program_name=prog_name_input
                )
                st.session_state["last_compilation_id"] = comp_id
            except Exception as e:
                st.error(f"Failed to record compilation into database: {e}")

    # Display Analysis Results
    curr_result: Optional[CompilationResult] = st.session_state.get("last_result")

    if curr_result:
        st.markdown("---")

        # Status Banner
        if curr_result.is_success:
            st.success(
                f"✅ **Compilation Successful!** {curr_result.token_count} tokens processed in {curr_result.duration_ms} ms. Zero errors detected."
            )
        else:
            st.error(
                f"❌ **Compilation Failed!** Detected {curr_result.error_count} error(s) during analysis ({curr_result.duration_ms} ms)."
            )

        # Tabbed Output Interface
        tab_tokens, tab_ast, tab_sym, tab_tac, tab_errors = st.tabs([
            f"🔍 Tokens ({curr_result.token_count})",
            "🌳 Syntax Tree (AST)",
            "📋 Symbol Table",
            "⚙️ Three-Address Code (TAC)",
            f"⚠️ Diagnostics ({curr_result.error_count})"
        ])

        with tab_tokens:
            tok_records = [t.to_dict() for t in curr_result.tokens if t.token_type.value != "EOF"]
            if tok_records:
                tok_df = pd.DataFrame(tok_records)
                st.dataframe(
                    tok_df[["line", "column", "token_type", "category", "lexeme", "value"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No tokens found.")

        with tab_ast:
            if curr_result.ast:
                ast_col1, ast_col2 = st.columns([1, 1])
                with ast_col1:
                    st.markdown("##### 🌳 Textual Hierarchical AST")
                    st.code(render_ast_text(curr_result.ast), language="text")

                with ast_col2:
                    st.markdown("##### 🎨 Visual AST Representation")
                    dot = render_ast_graphviz(curr_result.ast)
                    if dot:
                        try:
                            st.graphviz_chart(dot)
                        except Exception:
                            st.info("Visual diagram rendering unavailable; see hierarchical text AST on the left.")
                    else:
                        st.info("Install Graphviz binaries to view graphical node diagrams.")
            else:
                st.warning("Abstract Syntax Tree could not be formed due to syntax errors.")

        with tab_sym:
            if curr_result.symbol_table and curr_result.symbol_table.all_symbols():
                sym_list = curr_result.symbol_table.to_list()
                sym_df = pd.DataFrame(sym_list)
                st.dataframe(sym_df, use_container_width=True, hide_index=True)
            else:
                st.info("No variables declared or symbols resolved.")

        with tab_tac:
            if curr_result.tac_instructions:
                tac_text = "\n".join(curr_result.tac_instructions)
                st.code(tac_text, language="c")
                st.download_button(
                    label="💾 Download TAC (.tac)",
                    data=tac_text,
                    file_name="program_tac.tac",
                    mime="text/plain"
                )
            else:
                st.info("Intermediate code generation is paused until syntax and semantic errors are resolved.")

        with tab_errors:
            if curr_result.diagnostics:
                for diag in curr_result.diagnostics:
                    with st.container():
                        st.markdown(
                            f"**[{diag.phase.value}] Error {diag.error_code}** (Line {diag.line or '?'}, Col {diag.column or '?'})"
                        )
                        st.markdown(f"• **Message:** `{diag.message}`")
                        if diag.suggestion:
                            st.markdown(f"• 💡 **Suggestion:** {diag.suggestion}")
                        st.markdown("---")
            else:
                st.success("No errors found. Clean compilation!")


# -----------------------------------------------------------------------------
# SECTION C: TOKEN ANALYSIS
# -----------------------------------------------------------------------------

elif menu_option == "🔍 Token Analysis":
    st.title("🔍 Lexical Token Analysis")
    st.markdown("Deep inspection of source code tokenization, lexical classifications, and category distribution.")

    curr_result: Optional[CompilationResult] = st.session_state.get("last_result")

    if not curr_result or not curr_result.tokens:
        st.info("No active compilation result. Please run analysis in **Code Analyzer** first.")
    else:
        tokens_filtered = [t for t in curr_result.tokens if t.token_type.value != "EOF"]
        records = [t.to_dict() for t in tokens_filtered]
        df = pd.DataFrame(records)

        # Metrics row
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Tokens", len(tokens_filtered))
        c2.metric("Keywords", len(df[df["category"] == "Keyword"]) if not df.empty else 0)
        c3.metric("Identifiers", len(df[df["category"] == "Identifier"]) if not df.empty else 0)
        c4.metric("Literals", len(df[df["category"] == "Literal"]) if not df.empty else 0)

        st.markdown("---")

        col_table, col_chart = st.columns([3, 2])

        with col_table:
            st.subheader("📋 Tokens Table")
            category_filter = st.multiselect(
                "Filter by Category:",
                options=list(df["category"].unique()) if not df.empty else [],
                default=list(df["category"].unique()) if not df.empty else []
            )

            filtered_df = df[df["category"].isin(category_filter)] if not df.empty and category_filter else df
            st.dataframe(filtered_df[["line", "column", "token_type", "category", "lexeme"]], use_container_width=True, hide_index=True)

            # Export options
            csv_data = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Export Tokens as CSV", data=csv_data, file_name="tokens_report.csv", mime="text/csv")

        with col_chart:
            st.subheader("📊 Category Breakdown")
            if not df.empty:
                cat_counts = df["category"].value_counts().reset_index()
                cat_counts.columns = ["Category", "Count"]
                st.bar_chart(data=cat_counts.set_index("Category"))


# -----------------------------------------------------------------------------
# SECTION D: ERROR REPORT
# -----------------------------------------------------------------------------

elif menu_option == "⚠️ Error Report":
    st.title("⚠️ Compiler Diagnostic & Error Report")
    st.markdown("Centralized error diagnostics classified across Lexical, Syntax, and Semantic phases.")

    curr_result: Optional[CompilationResult] = st.session_state.get("last_result")

    if not curr_result:
        st.info("No active compilation result. Please run analysis in **Code Analyzer** first.")
    elif not curr_result.diagnostics:
        st.success("🎉 Outstanding! Zero errors detected in the current source code.")
    else:
        err_df = pd.DataFrame([d.to_dict() for d in curr_result.diagnostics])

        st.markdown(f"#### Total Issues Detected: `{len(curr_result.diagnostics)}`")

        for idx, row in err_df.iterrows():
            st.error(
                f"**[{row['phase']}] Error Code: `{row['error_code']}`** — Line {row['line'] or 'N/A'}, Column {row['column'] or 'N/A'}\n\n"
                f"**Message:** {row['message']}\n\n"
                f"💡 **Correction Advice:** {row['suggestion'] or 'Review language syntax.'}"
            )


# -----------------------------------------------------------------------------
# SECTION E: SAVED PROGRAMS
# -----------------------------------------------------------------------------

elif menu_option == "📁 Saved Programs":
    st.title("📁 Saved Programs Repository")
    st.markdown("Manage and search stored C-like programs in the persistent SQLite database.")

    search = st.text_input("🔍 Search programs by name or code keyword:", "")
    programs = repo.list_programs(search_query=search)

    if not programs:
        st.info("No saved programs found matching your search.")
    else:
        for prog in programs:
            with st.expander(f"📄 #{prog['id']} — {prog['name']} (Last updated: {prog['updated_at']})"):
                st.code(prog["source_code"], language="c")

                c_load, c_rename, c_del = st.columns([1, 1, 1])

                with c_load:
                    if st.button("📥 Load into Editor", key=f"load_{prog['id']}"):
                        st.session_state["source_code"] = prog["source_code"]
                        st.session_state["current_program_name"] = prog["name"]
                        st.session_state["current_program_id"] = prog["id"]
                        st.success(f"Loaded '{prog['name']}'! Go to 'Code Analyzer' to run it.")

                with c_rename:
                    new_title = st.text_input("New Name", value=prog["name"], key=f"rename_input_{prog['id']}")
                    if st.button("✏️ Rename", key=f"rename_{prog['id']}"):
                        repo.update_program(prog["id"], name=new_title)
                        st.success("Renamed!")
                        st.rerun()

                with c_del:
                    confirm = st.checkbox("Confirm Delete", key=f"confirm_{prog['id']}")
                    if st.button("🗑 Delete", key=f"del_{prog['id']}"):
                        if confirm:
                            repo.delete_program(prog["id"])
                            st.warning(f"Deleted program #{prog['id']}.")
                            st.rerun()
                        else:
                            st.error("Check 'Confirm Delete' box first.")


# -----------------------------------------------------------------------------
# SECTION F: COMPILATION HISTORY
# -----------------------------------------------------------------------------

elif menu_option == "📜 Compilation History":
    st.title("📜 Compilation History Log")
    st.markdown("Comprehensive audit trail of all previous compilation attempts stored in SQLite.")

    filter_status = st.selectbox("Filter Status:", ["All", "SUCCESS", "FAILED"])
    actual_filter = None if filter_status == "All" else filter_status

    history = repo.get_recent_compilations(limit=50, status_filter=actual_filter)

    if not history:
        st.info("No compilation history entries recorded yet.")
    else:
        hist_df = pd.DataFrame(history)
        st.dataframe(
            hist_df[["id", "program_name_snapshot", "status", "token_count", "error_count", "duration_ms", "started_at"]],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        st.subheader("🔍 Inspect Past Compilation Run")
        selected_id = st.selectbox(
            "Select Run ID to Inspect Details:",
            options=[h["id"] for h in history]
        )

        if st.button("Inspect Run Details"):
            details = repo.get_compilation_details(selected_id)
            if details:
                st.markdown(f"#### 📄 Program Snapshot: `{details['program_name_snapshot']}`")
                st.code(details["source_code_snapshot"], language="c")

                c_tok, c_err = st.columns(2)
                with c_tok:
                    st.markdown(f"**Tokens ({len(details['tokens'])})**")
                    if details["tokens"]:
                        st.dataframe(pd.DataFrame(details["tokens"]), use_container_width=True)
                with c_err:
                    st.markdown(f"**Errors ({len(details['errors'])})**")
                    if details["errors"]:
                        st.dataframe(pd.DataFrame(details["errors"]), use_container_width=True)
                    else:
                        st.success("Clean run with no errors.")

                if "TAC" in details.get("artifacts", {}):
                    st.markdown("**Intermediate Code (TAC) Generated:**")
                    st.code(details["artifacts"]["TAC"], language="c")


# -----------------------------------------------------------------------------
# SECTION G: ABOUT AND HELP
# -----------------------------------------------------------------------------

elif menu_option == "ℹ️ About & Help":
    st.title("ℹ️ About & Technical Documentation")
    st.markdown("### Smart Lexical Analyzer and Syntax Checker Using Python")

    st.markdown(
        """
        - **Institution:** Shri Sant Gajanan Maharaj College of Engineering, Shegaon
        - **Department:** Computer Science & Engineering
        - **Course:** Compiler Design — TEC Assignment (5CS221PC)
        - **Academic Session:** Autumn/Winter 2026–2027
        """
    )

    st.markdown("---")

    st.subheader("📖 Supported EBNF Grammar")
    st.code(
        """
        program         -> statement*
        statement       -> declaration
                        | assignment
                        | print_statement

        declaration     -> TYPE IDENTIFIER "=" expression ";"
        assignment      -> IDENTIFIER "=" expression ";"
        print_statement -> "print" "(" expression ")" ";"

        expression      -> term (("+" | "-") term)*
        term            -> factor (("*" | "/") factor)*
        factor          -> NUMBER
                        | IDENTIFIER
                        | "(" expression ")"
                        | unary_expression

        unary_expression -> ("+" | "-") factor

        TYPE            -> "int" | "float"
        NUMBER          -> INT_LITERAL | FLOAT_LITERAL
        """,
        language="ebnf"
    )

    st.markdown("---")

    st.subheader("🎯 Viva & Oral Defense Preparation Guide")
    with st.expander("Q1: What is the primary role of the Lexical Analyzer (Scanner)?"):
        st.write(
            "The lexical analyzer converts the raw stream of characters from the source code into a sequence of meaningful tokens "
            "(keywords, identifiers, literals, operators, separators), while filtering out whitespace and comments and keeping track of line and column positions."
        )

    with st.expander("Q2: Why use a Recursive-Descent Parser for this project?"):
        st.write(
            "Recursive-descent parsing is a top-down parsing technique where each non-terminal in the grammar is implemented as a dedicated Python function. "
            "It is highly readable, easily debugged, straightforward to explain during viva, and enables robust error recovery."
        )

    with st.expander("Q3: How does the parser handle operator precedence?"):
        st.write(
            "Precedence is enforced structurally by layering grammar production rules. Factors (parentheses, numbers, identifiers) have highest precedence, "
            "terms (multiplication, division) are evaluated next, and expressions (addition, subtraction) have lowest precedence."
        )

    with st.expander("Q4: What is the role of Three-Address Code (TAC)?"):
        st.write(
            "Three-Address Code is an intermediate representation where each instruction has at most one operator and at most three operand addresses. "
            "It linearizes nested syntax trees into sequential instructions using temporary variables (e.g. t1, t2), making machine code generation and optimization straightforward."
        )

