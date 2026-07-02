import streamlit as st
import time
import os
import pandas as pd
from pathlib import Path

# Constants and settings
from config.constants import APP_NAME, SUPPORTED_FILE_TYPES
from config.settings import LOG_DIR
from utils.file_utils import allowed_file, save_uploaded_file, get_file_hash
from utils.helpers import get_file_size_mb

# Pipeline and Services
from services.document_service import DocumentService
from services.chat_service import ChatService
from services.report_service import ReportService
from controllers.dashboard_controller import DashboardController
from logger.audit_logger import AuditLogger

# Page configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Fully hide the sidebar and its toggle arrow + premium global styles
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ---- HIDE SIDEBAR COMPLETELY ---- */
    section[data-testid="stSidebar"] {
        display: none !important;
        width: 0 !important;
        min-width: 0 !important;
    }
    /* Hide the collapse/expand toggle button */
    button[kind="header"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }
    /* Reclaim the space the sidebar normally occupies */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* ---- GLOBAL TYPOGRAPHY ---- */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ---- APP HEADER GRADIENT ---- */
    .app-header {
        background: linear-gradient(135deg, #0F2140 0%, #1A365D 60%, #2B6CB0 100%);
        color: white;
        padding: 24px 30px;
        border-radius: 14px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 18px;
    }
    .app-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .app-header p {
        margin: 4px 0 0;
        font-size: 0.95rem;
        opacity: 0.75;
    }

    /* ---- METRIC CARDS ---- */
    .metric-card {
        background: linear-gradient(135deg, #1A365D 0%, #2A4365 100%);
        color: white;
        padding: 22px 18px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        text-align: center;
        margin-bottom: 10px;
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    .metric-title {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        opacity: 0.75;
        font-weight: 600;
    }
    .metric-value {
        font-size: 2.4rem;
        font-weight: 700;
        margin: 10px 0 4px;
        line-height: 1;
    }
    .metric-subtitle {
        font-size: 0.75rem;
        opacity: 0.55;
    }

    /* ---- STREAMLIT TAB OVERRIDES ---- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #EBF4FF;
        padding: 6px 8px;
        border-radius: 10px;
        margin-bottom: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 600;
        font-size: 0.88rem;
        color: #2D3748;
        background: transparent;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background: white;
        color: #1A365D !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.12);
    }

    /* ---- REPORT CARD ---- */
    .report-card {
        border-left: 5px solid #2B6CB0;
        background-color: #F7FAFC;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "processed_docs" not in st.session_state:
    st.session_state.processed_docs = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_doc" not in st.session_state:
    st.session_state.selected_doc = None
if "compliance_threshold" not in st.session_state:
    st.session_state.compliance_threshold = 20
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "google/flan-t5-base"

# Service and Controller Instantiations
document_service = DocumentService()
chat_service = ChatService()
report_service = ReportService()
dashboard_controller = DashboardController()
audit_logger = AuditLogger()

# Premium gradient app header — no sidebar used
st.markdown("""
<div class="app-header">
    <span style="font-size:3rem;">🛡️</span>
    <div>
        <h1>MSentinel AI</h1>
        <p>AI-Powered Document Security &amp; Compliance Platform</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Top-level tab navigation — NO sidebar navigation used at all
tabs = st.tabs([
    "📊 System Dashboard",
    "📤 Upload & Process",
    "📄 Compliance Reports",
    "💬 Interactive RAG Chat",
    "🪵 Transaction Audit Logs",
    "⚙️ Platform Settings"
])

# ----------------- TAB 1: SYSTEM DASHBOARD -----------------
with tabs[0]:
    st.header("📊 Enterprise Analytics Dashboard")
    st.write("Real-time compliance rating, data leaks exposure summary, and processing speeds.")
    st.write("---")

    metrics = dashboard_controller.get_metrics(st.session_state.processed_docs)

    # Custom Styled Metrics Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Files Scanned</div>
            <div class="metric-value">{metrics['uploaded_files']}</div>
            <div class="metric-subtitle">Total documents processed</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Sensitive Entities</div>
            <div class="metric-value">{metrics['sensitive_data_count']}</div>
            <div class="metric-subtitle">Total leaks detected</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avg Compliance</div>
            <div class="metric-value">{metrics['avg_compliance_score']}%</div>
            <div class="metric-subtitle">Security rating</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, {'#C53030' if metrics['avg_risk_score'] >= st.session_state.compliance_threshold else '#2B6CB0'} 0%, #2D3748 100%)">
            <div class="metric-title">Avg Risk Score</div>
            <div class="metric-value">{metrics['avg_risk_score']}</div>
            <div class="metric-subtitle">Threshold: {st.session_state.compliance_threshold}</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avg Parse Time</div>
            <div class="metric-value">{metrics['avg_processing_time']}s</div>
            <div class="metric-subtitle">OCR / LLM Pipeline speed</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("---")

    if not st.session_state.processed_docs:
        st.info("💡 No documents have been scanned yet. Navigate to the **📤 Upload & Process** tab to get started!")
    else:
        # Visualizations Section
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            fig_pie = dashboard_controller.get_pie_chart(st.session_state.processed_docs)
            if fig_pie:
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.write("No categories to plot.")
        with col_chart2:
            fig_bar = dashboard_controller.get_bar_chart(st.session_state.processed_docs)
            if fig_bar:
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.write("No risk weights to plot.")

        st.write("---")
        
        # Timeline Chart
        st.subheader("Processing Log Timeline")
        fig_time = dashboard_controller.get_timeline_chart(Path(LOG_DIR) / "audit.csv")
        if fig_time:
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.caption("Not enough audit logging transactions available to plot timeline.")

        st.write("---")

        # Global Detected Entities Table
        st.subheader("Vulnerability Findings Log")
        df_entities = dashboard_controller.get_table(st.session_state.processed_docs)
        if not df_entities.empty:
            st.dataframe(
                df_entities,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("Clean Sheet! No sensitive variables or security credentials detected across the platform.")

# ----------------- TAB 2: UPLOAD & PROCESS -----------------
with tabs[1]:
    st.header("📤 Document Ingestion & Verification")
    st.write("Upload single or multiple text, CSV, or PDF documents. The AI security pipeline will execute automatically.")
    st.write("---")

    uploaded_files = st.file_uploader(
        "Ingest Documents",
        type=SUPPORTED_FILE_TYPES,
        accept_multiple_files=True,
        key="uploader"
    )

    if uploaded_files:
        st.success(f"Successfully selected {len(uploaded_files)} file(s). Click process to scan.")
        
        if st.button("🚀 Execute Security Deep Scan"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            for idx, uploaded_file in enumerate(uploaded_files):
                if uploaded_file.name in st.session_state.processed_docs:
                    progress_bar.progress((idx + 1) / len(uploaded_files))
                    continue

                status_text.write(f"Ingesting {uploaded_file.name}...")
                
                # Save file
                saved_path = save_uploaded_file(uploaded_file)
                file_hash = get_file_hash(saved_path)

                status_text.write(f"Running multi-layer scanning on {uploaded_file.name}...")
                
                start_time = time.time()
                
                # Execute pipeline processing
                doc = document_service.process_document(saved_path)
                
                elapsed_time = time.time() - start_time
                doc.processing_time = elapsed_time

                # Save to Session State
                st.session_state.processed_docs[uploaded_file.name] = doc
                if not st.session_state.selected_doc:
                    st.session_state.selected_doc = uploaded_file.name

                # Log Transaction to Audit Logs
                audit_logger.log_document(
                    filename=doc.original_name,
                    file_hash=file_hash,
                    proc_time=elapsed_time,
                    risk_score=doc.risk_score,
                    compliance_score=doc.compliance_score,
                    risk_level=doc.risk_level
                )

                progress_bar.progress((idx + 1) / len(uploaded_files))

            status_text.write("✅ Scanning completed successfully!")
            st.balloons()
            time.sleep(1)
            st.rerun()

    # List Current Ingested Files
    if st.session_state.processed_docs:
        st.subheader("Currently Processed Session Files")
        file_rows = []
        for doc in st.session_state.processed_docs.values():
            file_rows.append({
                "Document Name": doc.original_name,
                "File Size (MB)": get_file_size_mb(doc.saved_path),
                "OCR Applied": "Yes" if doc.ocr_used else "No",
                "Pages": doc.page_count,
                "Entities Found": len(doc.entities),
                "Risk Rating": doc.risk_level,
                "Compliance score": f"{doc.compliance_score}%",
                "Process Time": f"{doc.processing_time:.2f}s"
            })
        st.dataframe(
            pd.DataFrame(file_rows),
            use_container_width=True,
            hide_index=True
        )

# ----------------- TAB 3: COMPLIANCE REPORTS -----------------
with tabs[2]:
    st.header("📄 Document Security Reports")
    st.write("Analyze individual document profiles, export masked texts, and download PDF audit certificates.")
    st.write("---")

    if not st.session_state.processed_docs:
        st.warning("No files have been processed. Go to Upload & Process first.")
    else:
        # Document Selection Dropdown
        doc_names = list(st.session_state.processed_docs.keys())
        selected_name = st.selectbox(
            "Select Target Document for Verification", 
            doc_names, 
            index=doc_names.index(st.session_state.selected_doc) if st.session_state.selected_doc in doc_names else 0,
            key="report_doc_selector"
        )
        
        # Update selection in session state
        st.session_state.selected_doc = selected_name
        doc = st.session_state.processed_docs[selected_name]

        # Summary Row
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Risk Score", f"{doc.risk_score} / 100", delta=None)
        col2.metric("Compliance Rating", f"{doc.compliance_score}%", delta=None)
        col3.metric("Leaks Blocked", len(doc.entities), delta=None)
        col4.metric("Redactions Applied", doc.redaction_count, delta=None)

        st.write("---")

        # Multi-tab view: Original, Redacted, Compliance Report
        preview_tabs = st.tabs(["🔒 Redacted Preview", "📝 Compliance Report", "👁️ Original Scanned Text"])
        
        with preview_tabs[0]:
            st.subheader("Masked/Redacted Text Output")
            st.caption("All sensitive credentials and identifiers have been scrubbed based on active settings.")
            st.code(doc.masked_text or "[Empty Text]")
            
            # Downloads for Redacted Text
            redacted_path = report_service.get_redacted_path(doc)
            with open(redacted_path, "r", encoding="utf-8") as rf:
                redacted_data = rf.read()
            st.download_button(
                label="📥 Download Redacted Text Document",
                data=redacted_data,
                file_name=f"{doc.saved_path.stem}_redacted.txt",
                mime="text/plain",
                key="dl_redacted"
            )

        with preview_tabs[1]:
            st.subheader("Markdown Audit Certificate Preview")
            st.markdown(doc.report_markdown)
            
            # Downloads for Reports
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.download_button(
                    label="📥 Download Report (Markdown)",
                    data=doc.report_markdown,
                    file_name=f"{doc.saved_path.stem}_report.md",
                    mime="text/markdown",
                    key="dl_md_report"
                )
            with col_b2:
                # Generate PDF
                pdf_path = report_service.generate_pdf_report(doc)
                with open(pdf_path, "rb") as pf:
                    pdf_data = pf.read()
                st.download_button(
                    label="📥 Download Official Report (PDF)",
                    data=pdf_data,
                    file_name=f"{doc.saved_path.stem}_report.pdf",
                    mime="application/pdf",
                    key="dl_pdf_report"
                )

        with preview_tabs[2]:
            st.subheader("Original Extracted Raw Text")
            st.code(doc.cleaned_text or "[Empty Text]")

# ----------------- TAB 4: INTERACTIVE RAG CHAT -----------------
with tabs[3]:
    st.header("💬 Interactive Compliance Assistant")
    st.write("Query the indexed vectors using Semantic Search, Summarize documents, or compare compliance metrics.")
    st.write("---")

    if not st.session_state.processed_docs:
        st.warning("No documents are currently indexed in ChromaDB. Please process documents first.")
    else:
        # Split screen: Left side controls, Right side chat
        col_chat_ctrl, col_chat_area = st.columns([1, 2])
        
        with col_chat_ctrl:
            st.markdown("### Document Shortcuts")
            active_doc = st.selectbox("Focus Document", list(st.session_state.processed_docs.keys()), key="chat_focus_doc")
            
            col_act1, col_act2 = st.columns(2)
            
            # Summarize action
            if col_act1.button("📝 Summarize Doc", use_container_width=True):
                with st.spinner("Analyzing document chunks..."):
                    summary = chat_service.summarize(active_doc)
                    st.session_state.chat_history.append({"role": "user", "text": f"Generate a summary for: {active_doc}"})
                    st.session_state.chat_history.append({"role": "assistant", "text": summary, "sources": []})
                    audit_logger.log_query(f"Summary request: {active_doc}", summary, st.session_state.selected_model)

            # Risk audit action
            if col_act2.button("🔬 Audit Risks", use_container_width=True):
                with st.spinner("Scrutinizing vectors..."):
                    risk_report = chat_service.analyze_risks(active_doc)
                    st.session_state.chat_history.append({"role": "user", "text": f"Audit vulnerability risks for: {active_doc}"})
                    st.session_state.chat_history.append({"role": "assistant", "text": risk_report, "sources": []})
                    audit_logger.log_query(f"Risk analysis request: {active_doc}", risk_report, st.session_state.selected_model)
            
            st.write("---")
            st.markdown("### Compare Documents")
            docs_to_compare = st.multiselect("Select Documents", list(st.session_state.processed_docs.keys()), key="chat_compare_docs")
            comparison_aspect = st.text_input("Aspect to compare", "sensitive leaks and risk scores", key="chat_compare_aspect")
            
            if st.button("⚖️ Run Comparative Review", use_container_width=True):
                if len(docs_to_compare) < 2:
                    st.error("Select at least 2 files to compare.")
                else:
                    with st.spinner("Comparing document indices..."):
                        comp_result = chat_service.compare(docs_to_compare, comparison_aspect)
                        st.session_state.chat_history.append({"role": "user", "text": f"Compare {', '.join(docs_to_compare)} regarding '{comparison_aspect}'"})
                        st.session_state.chat_history.append({"role": "assistant", "text": comp_result, "sources": []})
                        audit_logger.log_query(f"Comparison: {docs_to_compare}", comp_result, st.session_state.selected_model)

        with col_chat_area:
            st.markdown("### Discussion Console")
            
            # Chat history container
            chat_container = st.container(height=400)
            with chat_container:
                for msg in st.session_state.chat_history:
                    if msg["role"] == "user":
                        with st.chat_message("user"):
                            st.write(msg["text"])
                    else:
                        with st.chat_message("assistant"):
                            st.write(msg["text"])
                            if "sources" in msg and msg["sources"]:
                                with st.expander("Show retrieved reference sources"):
                                    for src in msg["sources"]:
                                        st.write(f"📄 {src['document']} (Chunk {src['chunk']})")

            # Chat Input
            user_query = st.chat_input("Ask a compliance or document security question...", key="chat_user_input")
            if user_query:
                # Display user query
                with chat_container:
                    with st.chat_message("user"):
                        st.write(user_query)
                st.session_state.chat_history.append({"role": "user", "text": user_query})

                # Generate and display response
                with chat_container:
                    with st.chat_message("assistant"):
                        with st.spinner("Retrieving facts and generating compliance advisory..."):
                            answer, results = chat_service.ask(user_query)
                            st.write(answer)
                            
                            sources = []
                            if results and "metadatas" in results and results["metadatas"]:
                                sources = results["metadatas"][0]
                                with st.expander("Show retrieved reference sources"):
                                    for meta in sources:
                                        st.write(f"📄 {meta['document']} (Chunk {meta['chunk']})")

                st.session_state.chat_history.append({"role": "assistant", "text": answer, "sources": sources})
                audit_logger.log_query(user_query, answer, st.session_state.selected_model)
                st.rerun()

# ----------------- TAB 5: TRANSACTION AUDIT LOGS -----------------
with tabs[4]:
    st.header("🪵 Transaction Audit Trail")
    st.write("View the chronological log of system operations, scanned files, risk scoring, and security advisory actions.")
    st.write("---")

    csv_path = Path(LOG_DIR) / "audit.csv"
    if not csv_path.exists() or csv_path.stat().st_size == 0:
        st.info("No logs are recorded in the audit CSV file yet.")
    else:
        df_logs = pd.read_csv(csv_path)
        
        # Display logs
        st.subheader("Audited Platform Logs")
        st.dataframe(
            df_logs.sort_index(ascending=False),
            use_container_width=True
        )

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            with open(csv_path, "r", encoding="utf-8") as lf:
                csv_data = lf.read()
            st.download_button(
                label="📥 Export Full Audit Log (CSV)",
                data=csv_data,
                file_name="msentinel_audit_logs.csv",
                mime="text/csv",
                key="dl_audit_csv"
            )
        with col_dl2:
            log_txt_path = Path(LOG_DIR) / "audit.log"
            if log_txt_path.exists():
                with open(log_txt_path, "r", encoding="utf-8") as tf:
                    log_text = tf.read()
                st.download_button(
                    label="📥 Export Tech File Logs (.log)",
                    data=log_text,
                    file_name="msentinel_audit.log",
                    mime="text/plain",
                    key="dl_audit_log_txt"
                )

# ----------------- TAB 6: PLATFORM SETTINGS -----------------
with tabs[5]:
    st.header("⚙️ Global Security Configurations")
    st.write("Adjust models, sensitivity levels, and default detection boundaries.")
    st.write("---")

    # Risk threshold configuration
    st.subheader("Threshold Boundaries")
    threshold = st.slider(
        "Risk Rating Threshold",
        min_value=5,
        max_value=80,
        value=st.session_state.compliance_threshold,
        help="Documents with a total risk score exceeding this limit are flagged as Action Required.",
        key="settings_risk_slider"
    )
    st.session_state.compliance_threshold = threshold

    # Model selector
    st.subheader("Model Selections")
    selected_model = st.selectbox(
        "Active RAG Model Pipeline",
        ["google/flan-t5-base", "Custom Rule-Based Fallback"],
        index=0 if st.session_state.selected_model == "google/flan-t5-base" else 1,
        key="settings_model_selector"
    )
    st.session_state.selected_model = selected_model

    st.write("---")
    st.success("Configuration modifications saved for current session.")