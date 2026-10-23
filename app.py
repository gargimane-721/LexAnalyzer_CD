"""
Smart Multi-Language Compiler & Analyzer (C, Python, Java)
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
from compiler.adapters.manager import toolchain_manager
from database.db import DatabaseManager, db_manager
from database.repository import CompilerRepository

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Multi-Language Mini Compiler (C, Python, Java)",
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

# Default Starter Code by Language
DEFAULT_SNIPPETS = {
    "c": (
        "#include <stdio.h>\n\n"
        "int main() {\n"
        "    int x = 10;\n"
        "    int y = 20;\n"
        "    printf(\"%d\\n\", x + y);\n"
        "    return 0;\n"
        "}"
    ),
    "python": (
        "# Python 3 Script\n"
        "x = 10\n"
        "y = 20\n"
        "print(x + y)"
    ),
    "java": (
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        int x = 10;\n"
        "        int y = 20;\n"
        "        System.out.println(x + y);\n"
        "    }\n"
        "}"
    )
}

# Initialize Session State
if "selected_language" not in st.session_state:
    st.session_state["selected_language"] = "c"
if "source_code" not in st.session_state:
    st.session_state["source_code"] = DEFAULT_SNIPPETS["c"]
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
        expr_str = render_ast_text(node.expression, indent + 2) if node.expression else "None"
        return f"{prefix}DeclarationNode: {node.var_type} {node.identifier}\n{prefix}  Expression:\n{expr_str}"

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

    elif node_type == "StringLiteralNode":
        return f"{prefix}StringLiteralNode: \"{node.value}\""

    elif node_type == "VariableNode":
        return f"{prefix}VariableNode: {node.name}"

    elif node_type == "FunctionDefNode":
        params_str = ", ".join(node.parameters)
        body_str = render_ast_text(node.body, indent + 1) if node.body else f"{prefix}  (declaration only)"
        return f"{prefix}FunctionDefNode: {node.return_type} {node.name}({params_str})\n{body_str}"

    elif node_type == "ClassDefNode":
        return f"{prefix}ClassDefNode: {node.name}\n" + "\n".join(render_ast_text(m, indent + 1) for m in node.members)

    elif node_type == "BlockNode":
        lines = [f"{prefix}BlockNode:"]
        for s in node.statements:
            lines.append(render_ast_text(s, indent + 1))
        return "\n".join(lines)

    elif node_type == "GenericNode":
        details_str = ", ".join(f"{k}={v}" for k, v in node.details.items())
        return f"{prefix}{node.name}Node: {details_str}"

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
                if n.expression:
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

            elif tname == "FunctionDefNode":
                label = f"Function: {node.return_type} {node.name}()"
                dot.node(node_id, label, fillcolor="#4F46E5")
                if node.body:
                    bid = add_node(node.body)
                    dot.edge(node_id, bid)

            elif tname == "ClassDefNode":
                dot.node(node_id, f"Class: {node.name}", fillcolor="#BE185D")
                for m in node.members:
                    mid = add_node(m)
                    dot.edge(node_id, mid)

            elif tname == "BlockNode":
                dot.node(node_id, "Block", fillcolor="#334155")
                for s in n.statements:
                    sid = add_node(s)
                    dot.edge(node_id, sid)

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

            elif tname == "StringLiteralNode":
                dot.node(node_id, f"\"{n.value}\"", fillcolor="#059669")

            elif tname == "VariableNode":
                dot.node(node_id, f"Var: {n.name}", fillcolor="#D97706")

            elif tname == "GenericNode":
                label = f"{n.name}\n" + "\n".join(f"{k}: {v}" for k, v in list(n.details.items())[:2])
                dot.node(node_id, label, fillcolor="#6366F1")

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
    st.markdown("### ⚡ Multi-Language Compiler")
    st.caption("C • Python • Java")
    st.caption("**Subject:** 5CS221PC — Compiler Design TEC")
    st.caption("SSGMCE Shegaon • Academic Session 2026–2027")

    st.markdown("---")

    menu_option = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "💻 Code Analyzer & Runner",
            "🔍 Token Analysis",
            "⚠️ Error Report",
            "📁 Saved Programs",
            "📜 Compilation History",
            "ℹ️ About & Help"
        ],
        index=1
    )

    st.markdown("---")

    # Language Toolchain Status Widget
    st.markdown("#### 🛠 Detected Toolchains")
    toolchains = toolchain_manager.check_all_toolchains()

    for lang_k, tinfo in toolchains.items():
        lang_label = lang_k.upper()
        if tinfo["available"]:
            st.success(f"**{lang_label}:** {tinfo['name']} ({tinfo['version']})")
        else:
            st.warning(f"**{lang_label}:** {tinfo['name']} (Missing)")

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
        "<small style='color: #94A3B8;'>Department of Computer Science & Engineering<br>"
        "Third Year B.E. — Fifth Semester</small>",
        unsafe_allow_html=True
    )


# -----------------------------------------------------------------------------
# SECTION A: DASHBOARD
# -----------------------------------------------------------------------------

if menu_option == "📊 Dashboard":
    st.title("📊 Multi-Language Compiler Dashboard")
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
        st.subheader("🕒 Recent Compilation & Execution Activity")
        recent_history = repo.get_recent_compilations(limit=10)
        if recent_history:
            history_df = pd.DataFrame(recent_history)
            display_df = history_df[["id", "language", "program_name_snapshot", "status", "token_count", "error_count", "duration_ms", "started_at"]].copy()
            display_df.columns = ["Run ID", "Language", "Program Name", "Status", "Tokens", "Errors", "Duration (ms)", "Timestamp"]
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("No compilation history found yet. Head to **Code Analyzer & Runner** to compile your first program!")

    with col_info:
        st.subheader("🌐 Supported Languages & Toolchains")
        st.markdown(
            """
            - **C Language:** Lexical scanning, recursive descent parsing, TAC generation, and compilation via **GCC / Clang**.
            - **Python 3:** Tokenizer with indent/dedent tracking, AST parsing with `ast.parse()`, and isolated execution via **Python Interpreter**.
            - **Java:** Class structure parsing, annotations, and bytecode compilation/execution via **javac / java JDK**.
            """
        )

        st.markdown("##### 📊 Runs by Language")
        if stats.get("language_breakdown"):
            lang_df = pd.DataFrame(list(stats["language_breakdown"].items()), columns=["Language", "Runs"])
            st.bar_chart(lang_df.set_index("Language"))


# -----------------------------------------------------------------------------
# SECTION B: CODE ANALYZER & RUNNER
# -----------------------------------------------------------------------------

elif menu_option == "💻 Code Analyzer & Runner":
    st.title("💻 Multi-Language Code Analyzer & Runner")
    st.caption("Select a programming language, write or load source code, perform lexical & syntax analysis, and execute.")

    # Language Selection Row
    col_lang, col_preset, col_load_btn = st.columns([1.5, 3.5, 1])

    with col_lang:
        current_lang = st.session_state.get("selected_language", "c")
        lang_choice = st.selectbox(
            "Select Language:",
            ["C", "Python", "Java"],
            index=["c", "python", "java"].index(current_lang) if current_lang in ["c", "python", "java"] else 0,
            key="language_selector_sb"
        )
        new_lang_key = lang_choice.lower()
        if new_lang_key != st.session_state["selected_language"]:
            st.session_state["selected_language"] = new_lang_key
            st.session_state["source_code"] = DEFAULT_SNIPPETS.get(new_lang_key, "")
            st.session_state["last_result"] = None
            st.rerun()

    # Filter sample programs matching selected language
    curr_lang = st.session_state["selected_language"]
    matching_samples = [s for s in samples_data if s.get("language", "c").lower() == curr_lang]
    sample_labels = [f"{s['name']} ({s['expected_validity']})" for s in matching_samples]

    with col_preset:
        selected_sample_idx = st.selectbox(
            f"Load {curr_lang.upper()} Sample Preset:",
            range(len(sample_labels)),
            format_func=lambda idx: sample_labels[idx] if sample_labels else "No samples available",
            index=0 if sample_labels else 0,
            key="sample_selector_sb"
        )

    with col_load_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("📥 Load Sample", use_container_width=True):
            if matching_samples:
                item = matching_samples[selected_sample_idx]
                st.session_state["source_code"] = item["source_code"]
                st.session_state["current_program_name"] = item["name"]
                st.session_state["last_result"] = None
                st.rerun()

    # Code Editor Area
    source_code_input = st.text_area(
        f"Source Code Editor ({curr_lang.upper()}):",
        value=st.session_state.get("source_code", ""),
        height=240,
        placeholder=f"Write your {curr_lang.upper()} code here...",
        key="main_editor_textarea"
    )
    st.session_state["source_code"] = source_code_input

    # Action Toolbar
    col_btn_lex, col_btn_syn, col_btn_run, col_btn_save, col_btn_clear = st.columns([1.5, 1.5, 1.8, 1.3, 1])

    with col_btn_lex:
        btn_lex = st.button("🔍 Run Lexer", use_container_width=True)

    with col_btn_syn:
        btn_syn = st.button("🌳 Check Syntax", use_container_width=True)

    with col_btn_run:
        btn_run = st.button("🚀 Compile & Run", type="primary", use_container_width=True)

    with col_btn_save:
        btn_save = st.button("💾 Save", use_container_width=True)

    with col_btn_clear:
        btn_clear = st.button("🗑 Clear", use_container_width=True)

    # Program Label for Saving
    prog_name_input = st.text_input(
        "Program Name / Title:",
        value=st.session_state.get("current_program_name", f"My {curr_lang.upper()} Script"),
        key="prog_title_input"
    )
    st.session_state["current_program_name"] = prog_name_input

    # Button Event Handlers
    if btn_clear:
        st.session_state["source_code"] = ""
        st.session_state["last_result"] = None
        st.rerun()

    if btn_save:
        if not source_code_input.strip():
            st.warning("Cannot save empty source code.")
        else:
            new_id = repo.create_program(prog_name_input, source_code_input, language=curr_lang)
            st.session_state["current_program_id"] = new_id
            st.success(f"Program '{prog_name_input}' ({curr_lang.upper()}) saved with ID #{new_id}!")

    if btn_lex or btn_syn or btn_run:
        if not source_code_input.strip():
            st.warning("Please enter source code before running analysis.")
        else:
            should_execute = bool(btn_run)
            result = compile_source(
                source_code_input,
                language=curr_lang,
                execute=should_execute
            )
            st.session_state["last_result"] = result

            # Record compilation run into SQLite
            try:
                comp_id = repo.record_compilation(
                    result,
                    program_id=st.session_state.get("current_program_id"),
                    program_name=prog_name_input,
                    language=curr_lang
                )
                st.session_state["last_compilation_id"] = comp_id
            except Exception as e:
                st.error(f"Failed to record run into SQLite database: {e}")

    # Display Analysis & Execution Results
    curr_result: Optional[CompilationResult] = st.session_state.get("last_result")

    if curr_result:
        st.markdown("---")

        # Status Banner
        if curr_result.is_success:
            st.success(
                f"✅ **Analysis Successful!** [{curr_result.language.upper()}] Processed {curr_result.token_count} tokens in {curr_result.duration_ms} ms. Zero syntax errors."
            )
        else:
            st.error(
                f"❌ **Analysis Issues Found!** [{curr_result.language.upper()}] Detected {curr_result.error_count} error(s) ({curr_result.duration_ms} ms)."
            )

        # Tabbed Output Interface
        tab_exec, tab_tokens, tab_ast, tab_sym, tab_tac, tab_errors = st.tabs([
            "🚀 Execution Output",
            f"🔍 Tokens ({curr_result.token_count})",
            "🌳 Syntax Tree (AST)",
            "📋 Symbol Table",
            "⚙️ Intermediate Code (TAC)",
            f"⚠️ Diagnostics ({curr_result.error_count})"
        ])

        with tab_exec:
            st.markdown("### 🚀 Real Toolchain Execution Output")
            if curr_result.execution_result:
                er = curr_result.execution_result
                col_e1, col_e2, col_e3 = st.columns(3)
                col_e1.metric("Toolchain", er.toolchain_name)
                col_e2.metric("Exit Code", er.exit_code)
                col_e3.metric("Duration", f"{er.duration_ms} ms")

                st.caption(f"**Version:** {er.toolchain_version}")

                if er.success:
                    st.success("Execution completed successfully.")
                else:
                    st.error(f"Execution error or toolchain failure.")

                if er.stdout:
                    st.markdown("##### 📤 Standard Output (stdout)")
                    st.code(er.stdout, language="text")

                if er.stderr:
                    st.markdown("##### ⚠️ Standard Error (stderr)")
                    st.code(er.stderr, language="text")

                if er.guidance:
                    st.info(f"💡 **Guidance:**\n{er.guidance}")
            else:
                st.info("Click **'🚀 Compile & Run'** above to compile and execute this program using the configured language toolchain.")

        with tab_tokens:
            tok_records = [t.to_dict() for t in curr_result.tokens if getattr(t.token_type, "value", str(t.token_type)) != "EOF"]
            if tok_records:
                tok_df = pd.DataFrame(tok_records)
                st.dataframe(
                    tok_df[["line", "column", "token_type", "category", "lexeme", "value"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No tokens produced.")

        with tab_ast:
            if curr_result.ast:
                c_ast1, c_ast2 = st.columns([1, 1])
                with c_ast1:
                    st.markdown("##### 🌳 Hierarchical AST Representation")
                    st.code(render_ast_text(curr_result.ast), language="text")
                with c_ast2:
                    st.markdown("##### 🎨 Visual Node Diagram")
                    dot = render_ast_graphviz(curr_result.ast)
                    if dot:
                        try:
                            st.graphviz_chart(dot)
                        except Exception:
                            st.info("Visual diagram rendering unavailable. See text tree on the left.")
                    else:
                        st.info("Visual graph rendering not available for this node type.")
            else:
                st.warning("AST could not be formed due to syntax errors.")

        with tab_sym:
            if curr_result.symbol_table and curr_result.symbol_table.all_symbols():
                sym_list = curr_result.symbol_table.to_list()
                st.dataframe(pd.DataFrame(sym_list), use_container_width=True, hide_index=True)
            else:
                st.info("No symbols registered.")

        with tab_tac:
            if curr_result.tac_instructions:
                tac_text = "\n".join(curr_result.tac_instructions)
                st.code(tac_text, language="c")
                st.download_button(
                    label="💾 Download TAC (.tac)",
                    data=tac_text,
                    file_name=f"{curr_lang}_program.tac",
                    mime="text/plain"
                )
            else:
                st.info("Intermediate code generation (TAC) is active for arithmetic expressions, declarations, and assignments.")

        with tab_errors:
            if curr_result.diagnostics:
                for diag in curr_result.diagnostics:
                    with st.container():
                        st.markdown(
                            f"**[{diag.phase.value if hasattr(diag.phase, 'value') else str(diag.phase)}] Error `{diag.error_code}`** (Line {diag.line or '?'}, Col {diag.column or '?'})"
                        )
                        st.markdown(f"• **Message:** `{diag.message}`")
                        if diag.suggestion:
                            st.markdown(f"• 💡 **Suggestion:** {diag.suggestion}")
                        st.markdown("---")
            else:
                st.success("No errors found. Clean analysis!")


# -----------------------------------------------------------------------------
# SECTION C: TOKEN ANALYSIS
# -----------------------------------------------------------------------------

elif menu_option == "🔍 Token Analysis":
    st.title("🔍 Lexical Token Analysis")
    st.markdown("Deep inspection of source code tokenization, lexical classifications, and category distribution.")

    curr_result: Optional[CompilationResult] = st.session_state.get("last_result")

    if not curr_result or not curr_result.tokens:
        st.info("No active compilation result. Please run analysis in **Code Analyzer & Runner** first.")
    else:
        tokens_filtered = [t for t in curr_result.tokens if getattr(t.token_type, "value", str(t.token_type)) != "EOF"]
        records = [t.to_dict() for t in tokens_filtered]
        df = pd.DataFrame(records)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Language", curr_result.language.upper())
        c2.metric("Total Tokens", len(tokens_filtered))
        c3.metric("Keywords", len(df[df["category"] == "Keyword"]) if not df.empty else 0)
        c4.metric("Identifiers", len(df[df["category"] == "Identifier"]) if not df.empty else 0)

        st.markdown("---")

        col_table, col_chart = st.columns([3, 2])

        with col_table:
            st.subheader("📋 Tokens Table")
            categories = list(df["category"].unique()) if not df.empty else []
            selected_cats = st.multiselect("Filter by Category:", options=categories, default=categories)

            filtered_df = df[df["category"].isin(selected_cats)] if not df.empty and selected_cats else df
            st.dataframe(filtered_df[["line", "column", "token_type", "category", "lexeme"]], use_container_width=True, hide_index=True)

            csv_data = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(f"📥 Export {curr_result.language.upper()} Tokens (CSV)", data=csv_data, file_name=f"{curr_result.language}_tokens.csv", mime="text/csv")

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
    st.markdown("Centralized error diagnostics classified across Lexical, Syntax, Semantic, and Execution phases.")

    curr_result: Optional[CompilationResult] = st.session_state.get("last_result")

    if not curr_result:
        st.info("No active compilation result. Please run analysis in **Code Analyzer & Runner** first.")
    elif not curr_result.diagnostics:
        st.success(f"🎉 Clean run! Zero errors detected in the current {curr_result.language.upper()} source code.")
    else:
        st.markdown(f"#### Total Issues Detected: `{len(curr_result.diagnostics)}` for [{curr_result.language.upper()}]")

        for diag in curr_result.diagnostics:
            phase_val = diag.phase.value if hasattr(diag.phase, "value") else str(diag.phase)
            st.error(
                f"**[{phase_val}] Error Code: `{diag.error_code}`** — Line {diag.line or 'N/A'}, Column {diag.column or 'N/A'}\n\n"
                f"**Message:** {diag.message}\n\n"
                f"💡 **Correction Advice:** {diag.suggestion or 'Review language syntax.'}"
            )


# -----------------------------------------------------------------------------
# SECTION E: SAVED PROGRAMS
# -----------------------------------------------------------------------------

elif menu_option == "📁 Saved Programs":
    st.title("📁 Saved Programs Repository")
    st.markdown("Manage and search stored C, Python, and Java programs in the persistent SQLite database.")

    c_search, c_filter = st.columns([3, 1])
    with c_search:
        search = st.text_input("🔍 Search programs by name or code keyword:", "")
    with c_filter:
        lang_filter = st.selectbox("Filter by Language:", ["All", "C", "Python", "Java"])

    programs = repo.list_programs(search_query=search, language_filter=lang_filter)

    if not programs:
        st.info("No saved programs found matching your criteria.")
    else:
        for prog in programs:
            p_lang = prog.get("language", "c").upper()
            with st.expander(f"📄 #{prog['id']} [{p_lang}] — {prog['name']} (Updated: {prog['updated_at']})"):
                st.code(prog["source_code"], language=prog.get("language", "c").lower())

                c_load, c_rename, c_del = st.columns([1, 1, 1])

                with c_load:
                    if st.button("📥 Load into Editor", key=f"load_{prog['id']}"):
                        st.session_state["source_code"] = prog["source_code"]
                        st.session_state["current_program_name"] = prog["name"]
                        st.session_state["current_program_id"] = prog["id"]
                        st.session_state["selected_language"] = prog.get("language", "c").lower()
                        st.success(f"Loaded '{prog['name']}' ({p_lang}) into Code Analyzer!")

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
    st.markdown("Audit trail of all compilation and execution attempts stored in SQLite.")

    c_f1, c_f2 = st.columns(2)
    with c_f1:
        filter_status = st.selectbox("Filter Status:", ["All", "SUCCESS", "FAILED"])
    with c_f2:
        filter_lang = st.selectbox("Filter Language:", ["All", "C", "Python", "Java"])

    actual_status = None if filter_status == "All" else filter_status
    actual_lang = None if filter_lang == "All" else filter_lang

    history = repo.get_recent_compilations(limit=50, status_filter=actual_status, language_filter=actual_lang)

    if not history:
        st.info("No compilation history records found.")
    else:
        hist_df = pd.DataFrame(history)
        st.dataframe(
            hist_df[["id", "language", "program_name_snapshot", "status", "token_count", "error_count", "duration_ms", "started_at"]],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        st.subheader("🔍 Inspect Past Compilation Run")
        selected_id = st.selectbox("Select Run ID to Inspect Details:", options=[h["id"] for h in history])

        if st.button("Inspect Run Details"):
            details = repo.get_compilation_details(selected_id)
            if details:
                st.markdown(f"#### 📄 Program Snapshot: `{details['program_name_snapshot']}` [{details.get('language', 'c').upper()}]")
                st.code(details["source_code_snapshot"], language=details.get("language", "c").lower())

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
    st.markdown("### Smart Multi-Language Compiler & Syntax Checker (C, Python, Java)")

    st.markdown(
        """
        - **Institution:** Shri Sant Gajanan Maharaj College of Engineering, Shegaon
        - **Department:** Computer Science & Engineering
        - **Course:** Compiler Design — TEC Assignment (5CS221PC)
        - **Supported Languages:** C, Python 3, Java
        - **Academic Session:** Autumn/Winter 2026–2027
        """
    )

    st.markdown("---")

    st.subheader("🌐 Architecture & Language Specifications")

    with st.expander("1. C Language Specification"):
        st.markdown(
            """
            - **Lexer:** Keywords (`int`, `float`, `char`, `double`, `void`, `return`, `if`, `while`, etc.), preprocessor directives (`#include`, `#define`), strings, chars, multi-line comments `/* ... */`, and single-line `//`.
            - **Parser:** Hand-crafted recursive descent parsing functions (`main()`), declarations, assignments, arithmetic precedence, braces `{ ... }`, and semicolons.
            - **Toolchain:** Compiles with GCC / Clang if installed, with isolated subprocess execution and timeout protection.
            """
        )

    with st.expander("2. Python Language Specification"):
        st.markdown(
            """
            - **Lexer:** Python keywords (`def`, `class`, `if`, `elif`, `else`, `return`, `import`, etc.), triple-quoted strings, `#` comments, and significant indentation (`INDENT`, `DEDENT`, `NEWLINE`).
            - **Parser:** AST parsing with `ast.parse()` capturing indentation and block structure errors with beginner-friendly remediation advice.
            - **Toolchain:** Executed directly via configured Python 3 interpreter in an isolated subprocess.
            """
        )

    with st.expander("3. Java Language Specification"):
        st.markdown(
            """
            - **Lexer:** Java keywords (`class`, `public`, `static`, `void`, `String`, etc.), annotations (`@Override`), strings, chars, and comments (`//`, `/* */`, `/** */`).
            - **Parser:** Validates class declarations, `public static void main(String[] args)`, methods, `System.out.println`, semicolons, and balanced braces.
            - **Toolchain:** Compiles with `javac` and executes with `java` JDK in an isolated temporary directory.
            """
        )

    st.markdown("---")

    st.subheader("🎯 Viva & Oral Defense Preparation Guide")
    viva_qa = [
        ("Q1: How does your multi-language compiler differ from simply making one parser accept all languages?",
         "We implemented independent, language-specific lexers and parsers for each language. Python indentation rules and colon blocks are parsed by Python-specific modules, while C and Java brace blocks and semicolons are parsed by their respective checkers. This ensures valid syntax from one language is never confused with invalid syntax from another."),
        ("Q2: How do you handle Python's significant indentation in the lexer?",
         "Our PythonLexer maintains an indentation stack (initially [0]). When non-blank lines start, it computes the indentation level. If greater, it pushes the level and emits an INDENT token. If less, it pops levels and emits DEDENT tokens. If misaligned, it reports an indentation error diagnostic."),
        ("Q3: How is real toolchain compilation executed safely?",
         "Execution is never run inside the main application process. We use subprocess.run with strict 5.0-second timeouts, isolated temporary working directories, restricted environment variables, and output truncation to prevent infinite loop memory exhaustion."),
        ("Q4: What happens if a toolchain like GCC or JDK is not installed?",
         "The application checks toolchain availability before attempting execution and displays clear installation instructions (e.g. MinGW-w64 or Eclipse Adoptium JDK) instead of crashing.")
    ]

    for q, a in viva_qa:
        with st.expander(q):
            st.write(a)
