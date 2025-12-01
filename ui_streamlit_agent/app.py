"""
Vanna Insight Engine - Streamlit Frontend
A fully encapsulated, secure web interface for text-to-SQL generation and analysis.
Communicates exclusively via HTTP to the FastAPI backend.
"""

import streamlit as st
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from client import VannaAPIClient
import pandas as pd
from io import BytesIO

# Configure page
st.set_page_config(
    page_title="Vanna Insight Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #1f771f;
        color: white;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #771f1f;
        color: white;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #1f3f77;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


def reset_agent_chat_state() -> None:
    """Reset chat history and conversation identifier."""
    st.session_state.agent_chat_history = []
    st.session_state.agent_conversation_id = None


def _render_status_message(level: str, message: str, detail: Optional[str] = None) -> None:
    """Render a status notification."""
    level = (level or "info").lower()
    body = message if not detail else f"{message}\n\n{detail}"

    if level in {"error", "danger", "fail"}:
        st.error(body)
    elif level in {"warning", "warn"}:
        st.warning(body)
    elif level in {"success", "ok", "ready"}:
        st.success(body)
    else:
        st.info(body)


def render_simple_component(component: Dict[str, Any]) -> None:
    """Render a simple (text/link) component."""
    comp_type = (component.get("type") or "").lower()
    if comp_type == "text":
        if text := component.get("text"):
            st.caption(text)
    elif comp_type == "link":
        href = component.get("href") or component.get("url")
        label = component.get("text") or href
        if href:
            st.markdown(f"[{label}]({href})")
    else:
        st.json(component)


def render_rich_component(component: Dict[str, Any]) -> None:
    """Render a rich component payload emitted by the agent."""
    component_type = (component.get("type") or "").lower()
    data = component.get("data") or {}

    if component_type in {"rich_text", "text"}:
        content = data.get("content") or data.get("text")
        if content:
            st.markdown(content)
    elif component_type == "status_card":
        title = data.get("title") or "Status"
        description = data.get("description")
        status = data.get("status") or "info"
        _render_status_message(status, f"**{title}**", description)
    elif component_type in {"status_bar_update", "status_update"}:
        _render_status_message(
            data.get("status") or "info",
            data.get("message") or "Status update",
            data.get("detail"),
        )
    elif component_type == "notification":
        _render_status_message(
            data.get("level") or "info",
            data.get("message") or "Notification",
            data.get("description"),
        )
    elif component_type == "progress_display":
        progress = data.get("progress")
        if isinstance(progress, (int, float)):
            st.progress(max(0.0, min(float(progress), 1.0)))
        if detail := data.get("message"):
            st.caption(detail)
    elif component_type == "dataframe":
        rows = data.get("rows") or []
        if rows:
            st.dataframe(pd.DataFrame(rows))
        else:
            st.info("Query executed successfully. No rows returned.")
    elif component_type in {"card", "container"}:
        if title := data.get("title"):
            st.subheader(title)
        if body := data.get("body") or data.get("description"):
            st.write(body)
    elif component_type in {"log_viewer", "task_list", "task_tracker_update"}:
        st.json(data)
    else:
        st.json(component)

    for child in component.get("children") or []:
        render_rich_component(child)


def render_agent_chunk(chunk: Dict[str, Any]) -> None:
    """Render combined rich/simple chunk data."""
    if rich := chunk.get("rich"):
        render_rich_component(rich)
    if simple := chunk.get("simple"):
        render_simple_component(simple)


# Initialize session state
if "client" not in st.session_state:
    st.session_state.client = VannaAPIClient()
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.query_templates = []
    st.session_state.show_detailed_feedback = False
    st.session_state.generated_sql_result = None
    st.session_state.agent_chat_history = []
    st.session_state.agent_conversation_id = None


def render_login_page():
    """Render authentication page."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 class='main-header'>🔍 Vanna Insight Engine</h1>", unsafe_allow_html=True)
        st.markdown("### Text-to-SQL Platform")
        st.markdown("Convert natural language questions into SQL queries with AI")
        
        st.divider()
        
        with st.form("login_form"):
            st.markdown("#### Login to Continue")
            username = st.text_input(
                "Username or Email",
                value=os.getenv("DEFAULT_USERNAME", "admin"),
                key="login_username"
            )
            password = st.text_input(
                "Password",
                type="password",
                value=os.getenv("DEFAULT_PASSWORD", ""),
                key="login_password"
            )
            
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                with st.spinner("Authenticating..."):
                    if st.session_state.client.login(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.success("✓ Login successful!")
                        st.rerun()
                    else:
                        st.error("✗ Login failed. Check your credentials.")
        
        st.markdown("---")
        st.markdown("""
        ### About This Application
        
        This is the frontend interface for the **Vanna Insight Engine** - an AI-powered text-to-SQL backend.
        
        **Features:**
        - 🤖 Generate SQL from natural language
        - 🔧 Fix SQL errors automatically
        - 📚 Explain SQL in plain English
        - 💾 Query history and feedback
        - 🛡️ Secure JWT authentication
        
        **Backend Status:** [Check Health](#)
        """)


def render_main_app():
    """Render main application interface."""
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.client.logout()
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()
        
        st.divider()
        
        page = st.radio(
            "Navigation",
            [
                "SQL Generator",
                "Query Executor",
                "Query History",
                "Query Templates",
                "Agent Chat",
                "Admin",
            ],
        )
        
        st.divider()
        
        with st.expander("ℹ️ System Status"):
            health = st.session_state.client.health_check()
            if "status" in health and health["status"] == "healthy":
                st.success("Backend: Online")
            else:
                st.warning("Backend: Checking...")
            st.json(health)
    
    # Main content area
    st.markdown("<h1 class='main-header'>🔍 Vanna Insight Engine</h1>", unsafe_allow_html=True)
    
    if page == "SQL Generator":
        render_sql_generator()
    elif page == "Query Executor":
        render_query_executor()
    elif page == "Query History":
        render_query_history()
    elif page == "Query Templates":
        render_query_templates()
    elif page == "Agent Chat":
        render_agent_chat()
    elif page == "Admin":
        render_admin_panel()


def render_agent_chat():
    """Render the streaming Vanna Agent chat experience."""
    st.header("Agent Chat (Streaming)")
    st.caption(
        "Talk directly to the upgraded Vanna 2.x agent. Responses stream from the backend "
        "SSE endpoint and include full component payloads."
    )

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Start New Conversation", use_container_width=True):
            reset_agent_chat_state()
            st.rerun()

    conversation_label = st.session_state.agent_conversation_id or "New conversation"
    st.markdown(f"**Conversation ID:** `{conversation_label}`")
    st.divider()

    history = st.session_state.agent_chat_history
    if not history:
        st.info("Start typing below to begin a conversation with the agent.")
    else:
        for entry in history:
            if entry.get("kind") == "user":
                with st.chat_message("user"):
                    st.markdown(entry.get("message", ""))
            elif entry.get("kind") == "agent":
                with st.chat_message("assistant"):
                    render_agent_chunk(entry.get("chunk", {}))

    prompt = st.chat_input("Ask the agent something...")
    if not prompt:
        return

    # Append user message to history immediately for persistence.
    st.session_state.agent_chat_history.append({"kind": "user", "message": prompt})

    streamed_chunks: List[Dict[str, Any]] = []
    assistant_container = st.chat_message("assistant")
    streaming_placeholder = assistant_container.empty()

    try:
        for chunk in st.session_state.client.stream_agent_chat(
            prompt,
            conversation_id=st.session_state.agent_conversation_id,
            metadata={"source": "streamlit-ui"},
        ):
            if chunk_id := chunk.get("conversation_id"):
                st.session_state.agent_conversation_id = chunk_id
            streamed_chunks.append({"kind": "agent", "chunk": chunk})
            with streaming_placeholder.container():
                for partial in streamed_chunks:
                    render_agent_chunk(partial["chunk"])
    except RuntimeError as exc:
        streaming_placeholder.empty()
        st.session_state.agent_chat_history.pop()  # remove last user entry on failure
        st.error(str(exc))
        return

    streaming_placeholder.empty()
    st.session_state.agent_chat_history.extend(streamed_chunks)
    st.rerun()


def render_sql_generator():
    """Render SQL generation interface."""
    st.header("SQL Generator")
    st.markdown("Convert natural language into SQL queries")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        question = st.text_area(
            "Enter your question",
            placeholder="e.g., Show me the top 10 customers by order volume",
            height=100,
            key="sql_question"
        )
    
    with col2:
        st.markdown("#### Options")
        auto_execute = st.checkbox("Auto-execute", value=False)

    # Session storage for the last generated SQL result is initialized globally

    if st.button("Generate SQL", use_container_width=True, type="primary", key="btn_generate_sql"):
        if not question.strip():
            st.error("Please enter a question")
        else:
            # Check LLM readiness before invoking SQL generation
            health = st.session_state.client.health_check()
            providers_active = health.get("providers_active", 0)
            if providers_active < 1:
                st.error(
                    "LLM provider is not available. "
                    "Please verify LLM configuration in the backend."
                )
                st.json(health)
                return

            with st.spinner("Generating SQL..."):
                result = st.session_state.client.generate_sql(question)
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    # Persist the result so that Explain/Execute can be
                    # triggered in subsequent reruns without losing state.
                    st.session_state.generated_sql_result = result

    # Render the last generated SQL (if any)
    generated = st.session_state.get("generated_sql_result")
    if generated:
        sql_code = generated.get("sql", "")
        st.subheader("Generated SQL")
        st.code(sql_code, language="sql")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📋 Copy", use_container_width=True, key="btn_copy_sql"):
                st.toast("SQL copied to clipboard!")

        with col2:
            if st.button("📖 Explain", use_container_width=True, key="btn_explain_sql"):
                # Check LLM readiness before explanation
                health = st.session_state.client.health_check()
                providers_active = health.get("providers_active", 0)
                if providers_active < 1:
                    st.error(
                        "LLM provider is not available. "
                        "Please verify LLM configuration in the backend."
                    )
                    st.json(health)
                else:
                    with st.spinner("Generating explanation..."):
                        explain_result = st.session_state.client.explain_sql(sql_code)
                        if "explanation" in explain_result:
                            st.markdown(explain_result["explanation"])
                        elif "error" in explain_result:
                            st.error(explain_result["error"])

        with col3:
            if st.button("▶️ Execute", use_container_width=True, key="btn_execute_sql"):
                # Check database connectivity before execution
                health = st.session_state.client.health_check()
                deps = health.get("dependencies", {})
                if not deps.get("postgres", False):
                    st.error(
                        "Database is not reachable. "
                        "Please ensure the Postgres container is healthy."
                    )
                    st.json(health)
                else:
                    with st.spinner("Executing query..."):
                        exec_result = st.session_state.client.execute_sql(sql_code, question)
                        if "error" in exec_result:
                            st.error(f"Execution failed: {exec_result['error']}")

                            # Add SQL fixing option when execution fails
                            st.divider()
                            st.markdown("### 🔧 SQL Error Assistance")
                            col_fix1, col_fix2 = st.columns(2)

                            with col_fix1:
                                if st.button("🔧 Fix SQL Automatically", use_container_width=True, key="btn_fix_sql"):
                                    with st.spinner("Analyzing and fixing SQL..."):
                                        fix_result = st.session_state.client.fix_sql(sql_code, exec_result["error"])
                                        if "error" in fix_result:
                                            st.error(f"Could not fix SQL: {fix_result['error']}")
                                        else:
                                            fixed_sql = fix_result.get("sql", "")
                                            st.success("✓ SQL fixed successfully!")
                                            st.code(fixed_sql, language="sql")

                                            # Allow user to use the fixed SQL
                                            if st.button("✅ Use Fixed SQL", key="btn_use_fixed_sql"):
                                                st.session_state.generated_sql_result = {
                                                    **generated,
                                                    "sql": fixed_sql
                                                }
                                                st.rerun()

                            with col_fix2:
                                if st.button("🔍 Validate SQL Syntax", use_container_width=True, key="btn_validate_sql"):
                                    with st.spinner("Validating SQL..."):
                                        validate_result = st.session_state.client.validate_sql(sql_code)
                                        if "error" in validate_result:
                                            st.error(f"Validation failed: {validate_result['error']}")
                                        else:
                                            is_valid = validate_result.get("is_valid", False)
                                            issues = validate_result.get("issues", [])

                                            if is_valid:
                                                st.success("✓ SQL syntax is valid")
                                            else:
                                                st.warning("⚠️ SQL validation issues found:")
                                                for issue in issues:
                                                    severity = issue.get("severity", "unknown")
                                                    message = issue.get("message", "Unknown issue")
                                                    if severity == "error":
                                                        st.error(f"Error: {message}")
                                                    elif severity == "warning":
                                                        st.warning(f"Warning: {message}")
                                                    else:
                                                        st.info(f"Info: {message}")
                        else:
                            st.success("Query executed successfully!")
                            results = exec_result.get("results", [])
                            if results:
                                st.dataframe(results)

                                # Add export functionality
                                st.divider()
                                st.markdown("### 📥 Export Results")
                                col_exp1, col_exp2, col_exp3 = st.columns(3)

                                import pandas as pd
                                df = pd.DataFrame(results)

                                with col_exp1:
                                    csv = df.to_csv(index=False)
                                    st.download_button(
                                        label="📄 Download CSV",
                                        data=csv,
                                        file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        mime="text/csv",
                                        use_container_width=True,
                                        key="download_csv"
                                    )

                                with col_exp2:
                                    json_data = df.to_json(orient="records", indent=2)
                                    st.download_button(
                                        label="📋 Download JSON",
                                        data=json_data,
                                        file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                        mime="application/json",
                                        use_container_width=True,
                                        key="download_json"
                                    )

                                with col_exp3:
                                    buffer = BytesIO()
                                    df.to_excel(buffer, index=False, engine='openpyxl')
                                    buffer.seek(0)
                                    st.download_button(
                                        label="📊 Download Excel",
                                        data=buffer,
                                        file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        use_container_width=True,
                                        key="download_excel"
                                    )
                            else:
                                st.info("Query returned no results")

        # Template and Feedback section
        st.divider()
        col_temp, col_feed = st.columns(2)

        with col_temp:
            st.subheader("📚 Save as Template")
            if st.button("⭐ Save Query", use_container_width=True, key="btn_save_template"):
                st.info("Switch to 'Query Templates' page to save this query as a reusable template.")

        with col_feed:
            st.subheader("Feedback")

            # Quick feedback buttons
            st.markdown("**Quick Feedback:**")
            quick_col1, quick_col2, quick_col3 = st.columns(3)

            with quick_col1:
                if st.button("👍 Helpful", use_container_width=True, key="quick_helpful"):
                    query_id = generated.get("query_id", "unknown")
                    feedback_result = st.session_state.client.submit_feedback(
                        query_id, question, "Quick feedback: Helpful", 5
                    )
                    if "error" not in feedback_result:
                        st.success("✓ Thanks for the positive feedback!")
                    else:
                        st.error("Could not submit feedback")

            with quick_col2:
                if st.button("👎 Not Helpful", use_container_width=True, key="quick_not_helpful"):
                    query_id = generated.get("query_id", "unknown")
                    feedback_result = st.session_state.client.submit_feedback(
                        query_id, question, "Quick feedback: Not helpful", 1
                    )
                    if "error" not in feedback_result:
                        st.success("✓ Thanks for the feedback!")
                    else:
                        st.error("Could not submit feedback")

            with quick_col3:
                if st.button("💡 Suggest Improvement", use_container_width=True, key="quick_suggest"):
                    st.session_state.show_detailed_feedback = True
                    st.rerun()

            # Detailed feedback (expandable)
            if st.session_state.get("show_detailed_feedback", False):
                st.markdown("---")
                st.markdown("**Detailed Feedback:**")
                feedback = st.text_area("Help us improve (optional)", key="feedback_text", height=80)
                rating = st.slider("Rate this result", 1, 5, 3, key="feedback_rating")

                submit_col1, submit_col2 = st.columns([1, 1])

                with submit_col1:
                    if st.button("Submit Feedback", key="btn_submit_feedback", use_container_width=True):
                        query_id = generated.get("query_id", "unknown")
                        feedback_result = st.session_state.client.submit_feedback(
                            query_id, question, feedback, rating
                        )
                        if "error" not in feedback_result:
                            st.success("✓ Thank you for your detailed feedback!")
                            st.session_state.show_detailed_feedback = False
                            st.rerun()
                        else:
                            st.warning("Could not submit feedback")

                with submit_col2:
                    if st.button("Cancel", key="btn_cancel_feedback", use_container_width=True):
                        st.session_state.show_detailed_feedback = False
                        st.rerun()


def render_query_executor():
    """Render direct SQL execution interface."""
    st.header("Query Executor")
    st.markdown("Execute SQL queries and view results")
    
    sql_query = st.text_area(
        "Enter SQL query",
        placeholder="SELECT * FROM table_name LIMIT 10",
        height=150,
        key="sql_execute"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶️ Execute Query", use_container_width=True, type="primary", key="btn_execute_query_executor"):
            if not sql_query.strip():
                st.error("Please enter a SQL query")
            else:
                # Check database connectivity via health endpoint
                health = st.session_state.client.health_check()
                deps = health.get("dependencies", {})
                if not deps.get("postgres", False):
                    st.error(
                        "Database is not reachable. "
                        "Please ensure the Postgres container is healthy."
                    )
                    st.json(health)
                else:
                    with st.spinner("Executing query..."):
                        result = st.session_state.client.execute_sql(sql_query)

                        if "error" in result:
                            st.error(f"Error: {result['error']}")
                        else:
                            st.success("Query executed successfully")
                            results = result.get("results", [])
                            if results:
                                st.dataframe(results)
                            else:
                                st.info("Query returned no results")

    with col2:
        if st.button("📖 Explain", use_container_width=True, key="btn_explain_query_executor"):
            if not sql_query.strip():
                st.error("Please enter a SQL query")
            else:
                # Check LLM readiness before explanation
                health = st.session_state.client.health_check()
                providers_active = health.get("providers_active", 0)
                if providers_active < 1:
                    st.error(
                        "LLM provider is not available. "
                        "Please verify LLM configuration in the backend."
                    )
                    st.json(health)
                else:
                    with st.spinner("Generating explanation..."):
                        result = st.session_state.client.explain_sql(sql_query)
                        if "explanation" in result:
                            st.markdown(result["explanation"])
                        elif "error" in result:
                            st.error(result["error"])


def render_query_history():
    """Render query history interface."""
    st.header("Query History")
    st.markdown("Your recent SQL queries")
    
    with st.spinner("Loading history..."):
        history_result = st.session_state.client.get_query_history()
        
        if "error" in history_result:
            st.error(f"Error: {history_result['error']}")
        else:
            queries = history_result.get("queries", [])
            
            if not queries:
                st.info("No queries in history yet")
            else:
                for query in queries:
                    with st.expander(f"📝 {query.get('question', 'Query')} - {query.get('created_at', '')}"):
                        st.code(query.get("sql", ""), language="sql")
                        st.caption(f"Executed: {query.get('executed_at', 'Not executed')}")
                        
                        if st.button("Re-use", key=f"reuse_{query.get('id')}"):
                            st.session_state.sql_question = query.get("question", "")
                            st.rerun()


def render_query_templates():
    """Render query templates interface."""
    st.header("Query Templates")
    st.markdown("Save and manage your frequently used queries")

    # Template management section
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📚 Your Templates")

        if not st.session_state.query_templates:
            st.info("No templates saved yet. Save queries from the SQL Generator to create templates.")
        else:
            for i, template in enumerate(st.session_state.query_templates):
                with st.expander(f"⭐ {template['name']} - {template['created_at']}"):
                    st.markdown(f"**Question:** {template['question']}")
                    st.code(template['sql'], language="sql")
                    st.caption(f"Tags: {', '.join(template.get('tags', []))}")

                    col_use, col_edit, col_delete = st.columns(3)

                    with col_use:
                        if st.button("🚀 Use Template", key=f"use_template_{i}"):
                            st.session_state.sql_question = template['question']
                            st.session_state.generated_sql_result = {
                                "sql": template['sql'],
                                "question": template['question']
                            }
                            st.success("Template loaded! Switch to SQL Generator to use it.")
                            st.rerun()

                    with col_edit:
                        if st.button("✏️ Edit", key=f"edit_template_{i}"):
                            st.session_state.editing_template = i
                            st.rerun()

                    with col_delete:
                        if st.button("🗑️ Delete", key=f"delete_template_{i}"):
                            st.session_state.query_templates.pop(i)
                            st.success("Template deleted!")
                            st.rerun()

    with col2:
        st.subheader("➕ Create Template")

        # Check if we have a generated SQL to save
        generated = st.session_state.get("generated_sql_result")
        if generated:
            st.success("✓ Generated SQL available to save as template!")

            with st.form("save_template_form"):
                template_name = st.text_input("Template Name", key="template_name")
                template_question = st.text_input("Question", value=generated.get("question", ""), key="template_question")
                template_tags = st.text_input("Tags (comma-separated)", key="template_tags")

                if st.form_submit_button("💾 Save as Template", use_container_width=True):
                    if template_name.strip():
                        new_template = {
                            "name": template_name.strip(),
                            "question": template_question.strip(),
                            "sql": generated.get("sql", ""),
                            "tags": [tag.strip() for tag in template_tags.split(",") if tag.strip()],
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        st.session_state.query_templates.append(new_template)
                        st.success(f"Template '{template_name}' saved!")
                        st.rerun()
                    else:
                        st.error("Please provide a template name")
        else:
            st.info("Generate some SQL first, then come back here to save it as a template.")

        # Quick templates section
        st.divider()
        st.subheader("⚡ Quick Templates")

        quick_templates = [
            {
                "name": "Count Records",
                "question": "How many records are in the table?",
                "sql": "SELECT COUNT(*) FROM your_table_name;"
            },
            {
                "name": "Top 10 Records",
                "question": "Show me the top 10 records",
                "sql": "SELECT * FROM your_table_name LIMIT 10;"
            },
            {
                "name": "Column Names",
                "question": "What are the column names in the table?",
                "sql": "SELECT column_name FROM information_schema.columns WHERE table_name = 'your_table_name';"
            }
        ]

        for template in quick_templates:
            if st.button(f"📋 {template['name']}", key=f"quick_{template['name']}", use_container_width=True):
                st.session_state.sql_question = template['question']
                st.session_state.generated_sql_result = {
                    "sql": template['sql'],
                    "question": template['question']
                }
                st.success(f"Quick template '{template['name']}' loaded! Switch to SQL Generator.")
                st.rerun()


def render_admin_panel():
    """Render admin panel (admin users only)."""
    st.header("Admin Panel")
    st.markdown("System configuration and management")
    
    with st.spinner("Loading configuration..."):
        config = st.session_state.client.get_config()
        
        if "error" in config:
            error_msg = config["error"]
            if "Unauthorized" in error_msg:
                st.error("You must log in again to access the admin panel.")
            elif "Access denied" in error_msg:
                st.error("Only administrators can access this panel.")
            elif "Endpoint not found" in error_msg:
                st.error("Admin API endpoint is not available. Please check backend configuration.")
            else:
                st.error(f"Admin panel error: {error_msg}")
        else:
            st.subheader("System Configuration")
            st.json(config)

            # Full Admin Panel button
            backend_url = st.session_state.client.backend_url
            admin_dashboard_url = f"{backend_url}/admin/dashboard"
            st.markdown("### 🔗 Full Admin Dashboard")
            st.markdown(f'<a href="{admin_dashboard_url}" target="_blank" style="text-decoration: none;"><button style="background-color: #FF6B6B; color: white; border: none; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 4px;">Open Full Admin Panel</button></a>', unsafe_allow_html=True)

            llm_cfg = config.get("llm")
            if llm_cfg:
                st.divider()
                st.subheader("LLM Configuration")

                active_provider = llm_cfg.get("provider", "unknown")
                providers_available = llm_cfg.get("providers_available", [])
                provider_block = llm_cfg.get(active_provider, {}) if isinstance(active_provider, str) else {}

                active_model = provider_block.get("model_name") or provider_block.get(
                    "deployment"
                ) or provider_block.get("model_id")

                st.markdown(
                    f"**Active provider:** `{active_provider}`"
                )
                if active_model:
                    st.markdown(f"**Active model:** `{active_model}`")

                if active_provider == "ollama":
                    base_url = provider_block.get("base_url", "")
                    if base_url:
                        st.markdown(f"**Base URL:** `{base_url}`")

                st.markdown("---")
                st.markdown("### Change LLM Provider / Model")

                selected_provider = st.selectbox(
                    "Provider",
                    providers_available or [active_provider],
                    index=(providers_available or [active_provider]).index(active_provider)
                    if active_provider in (providers_available or [active_provider])
                    else 0,
                    key="llm_provider_select",
                )

                suggested_model = ""
                selected_block = llm_cfg.get(selected_provider, {})
                if isinstance(selected_block, dict):
                    suggested_model = (
                        selected_block.get("model_name")
                        or selected_block.get("deployment")
                        or selected_block.get("model_id")
                        or ""
                    )

                new_model = st.text_input(
                    "Model / deployment name",
                    value=suggested_model,
                    key="llm_model_override",
                )

                if st.button("Apply LLM selection (instructions)", key="btn_apply_llm_selection"):
                    st.info(
                        "لتفعيل الاختيار الجديد، حدّث متغيرات البيئة في backend ثم أعد تشغيل الخدمة.\n\n"
                        f"- `LLM_PROVIDER={selected_provider}`\n"
                        + (f"- نموذج المزود (مثال): `{new_model}`\n" if new_model else "")
                        + "- بعد التعديل، نفّذ إعادة تشغيل للحاويات (./run.sh --clean --build ثم ./run.sh)."
                    )

            # Connectivity checks
            st.divider()
            st.subheader("Connectivity Checks")

            diag_col1, diag_col2, diag_col3 = st.columns(3)

            with diag_col1:
                if st.button("🔍 Test LLM Connectivity", use_container_width=True, key="btn_test_llm"):
                    with st.spinner("Testing LLM connectivity..."):
                        health = st.session_state.client.health_check()
                        providers_active = health.get("providers_active", 0)
                        if providers_active >= 1:
                            st.success(
                                f"LLM is available (providers_active={providers_active})."
                            )
                        else:
                            st.error("LLM provider is not available.")
                        st.json(health)

            with diag_col2:
                if st.button("🗄 Test System DB (PostgreSQL)", use_container_width=True, key="btn_test_system_db"):
                    with st.spinner("Testing database connectivity..."):
                        result = st.session_state.client.execute_sql("SELECT 1 AS ok")
                        if "error" in result:
                            st.error(f"System DB test failed: {result['error']}")
                        else:
                            st.success("System DB connectivity OK.")
                            st.json(result.get("results", result))

            with diag_col3:
                if st.button("📁 Test User DB (Target)", use_container_width=True, key="btn_test_user_db"):
                    with st.spinner("Testing user/target database connectivity..."):
                        t_health = st.session_state.client.check_target_db_health()
                        status = t_health.get("status", "unknown")
                        if status == "healthy":
                            st.success("Target (user) database is reachable.")
                        elif status == "disabled":
                            st.warning(t_health.get("message", "Target DB not configured."))
                        else:
                            st.error("Target database health check failed.")
                        st.json(t_health)

            st.divider()
            st.subheader("🔧 Custom Target Database Tester")

            st.markdown(
                "استخدم هذا النموذج لاختبار الاتصال بأي قاعدة بيانات مستخدم "
                "دون حفظ بيانات الاتصال في النظام. الاتصال يُستخدم للاختبار فقط."
            )

            db_type = st.selectbox(
                "Database type",
                ["sqlite", "postgresql", "mssql", "oracle"],
                index=0,
                key="custom_target_db_type",
            )

            input_mode = st.radio(
                "Configuration mode",
                ["Connection URL", "Individual fields"],
                index=0,
                key="custom_target_db_mode",
                horizontal=True,
            )

            payload: Dict[str, Any] = {"db_type": db_type}

            if input_mode == "Connection URL":
                conn_url = st.text_input(
                    "SQLAlchemy connection URL",
                    placeholder=(
                        "مثال PostgreSQL: postgresql+psycopg2://user:pass@host:5432/dbname "
                        "أو SQLite: sqlite:////path/to/file.db"
                    ),
                    key="custom_target_db_url",
                )
                if conn_url:
                    payload["connection_url"] = conn_url
            else:
                if db_type == "sqlite":
                    file_path = st.text_input(
                        "SQLite file path",
                        placeholder="/path/to/user_database.db",
                        key="custom_target_db_sqlite_path",
                    )
                    if file_path:
                        payload["file_path"] = file_path
                else:
                    col_host, col_port = st.columns(2)
                    with col_host:
                        host = st.text_input(
                            "Host",
                            placeholder="db.example.com",
                            key="custom_target_db_host",
                        )
                    with col_port:
                        default_port = (
                            5432 if db_type == "postgresql" else 1433 if db_type == "mssql" else 1521
                        )
                        port = st.number_input(
                            "Port",
                            min_value=1,
                            max_value=65535,
                            value=default_port,
                            key="custom_target_db_port",
                        )

                    username = st.text_input(
                        "Username",
                        placeholder="db_user",
                        key="custom_target_db_username",
                    )
                    password = st.text_input(
                        "Password",
                        type="password",
                        key="custom_target_db_password",
                    )
                    database = st.text_input(
                        "Database name",
                        placeholder="dbname (or service/SID for Oracle)",
                        key="custom_target_db_database",
                    )

                    if host:
                        payload["host"] = host
                    if port:
                        payload["port"] = int(port)
                    if username:
                        payload["username"] = username
                    if password:
                        payload["password"] = password
                    if database:
                        payload["database"] = database

                    if db_type == "mssql":
                        driver = st.text_input(
                            "ODBC driver (optional)",
                            placeholder="ODBC Driver 18 for SQL Server",
                            key="custom_target_db_driver",
                        )
                        if driver:
                            payload["driver"] = driver

            if st.button(
                "🔌 Test Custom Target DB Connection", key="btn_test_custom_target_db"
            ):
                with st.spinner("Testing custom Target DB connection..."):
                    result = st.session_state.client.test_target_db_connection(payload)
                    if "error" in result:
                        st.error(f"Connection test failed: {result['error']}")
                    else:
                        status_val = result.get("status", "unknown")
                        if status_val == "healthy":
                            st.success("Custom Target DB connection is healthy.")
                        else:
                            st.warning(f"Connection status: {status_val}")
                    st.json(result)

            st.divider()
            st.subheader("🤖 AI Model Management")

            model_col1, model_col2 = st.columns(2)

            with model_col1:
                if st.button("🚀 Train Model", use_container_width=True, type="secondary", key="btn_train_model"):
                    with st.spinner("Starting model training on approved feedback..."):
                        train_result = st.session_state.client.train_model()
                        if "error" in train_result:
                            st.error(f"Training failed: {train_result['error']}")
                        else:
                            st.success("✓ Model training started!")
                            st.info(f"Training ID: {train_result.get('training_id', 'Unknown')}")
                            st.json(train_result)

            with model_col2:
                if st.button("📊 Training Status", use_container_width=True, key="btn_training_status"):
                    st.info("Training status monitoring will be available in future updates.")

            st.divider()
            st.subheader("Admin Actions")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("📊 Feedback Metrics (Planned)", use_container_width=True, key="btn_feedback_metrics"):
                    with st.spinner("Fetching feedback metrics (planned feature)..."):
                        metrics = st.session_state.client.get_feedback_metrics()
                        st.info(metrics.get("message", "Feedback metrics feature is planned."))
                        st.json(metrics)

            with col2:
                if st.button("🗓 Scheduled Reports (Planned)", use_container_width=True, key="btn_scheduled_reports"):
                    with st.spinner("Listing scheduled reports (planned feature)..."):
                        reports = st.session_state.client.list_scheduled_reports()
                        st.info(reports.get("message", "Scheduled reports feature is planned."))
                        st.json(reports)

            with col3:
                if st.button("✅ Approve SQL (Planned)", use_container_width=True, key="btn_approve_sql"):
                    with st.spinner("Checking SQL approval feature (planned)..."):
                        approval = st.session_state.client.approve_sql_feature_info()
                        st.info(approval.get("message", "SQL approval feature is planned."))
                        st.json(approval)


def main():
    """Main application entry point."""
    # Check authentication
    if not st.session_state.authenticated:
        render_login_page()
    else:
        render_main_app()


if __name__ == "__main__":
    main()
