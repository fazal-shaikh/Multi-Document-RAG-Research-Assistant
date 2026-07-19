import re
import os

app_path = r"c:\Users\Lenovo\OneDrive\Desktop\Multi-Document RAG Research Assistant\app.py"
with open(app_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update the CSS Block
css_start = content.find("st.markdown(\"\"\"\n<style>")
css_end = content.find("</style>\n\"\"\", unsafe_allow_html=True)") + len("</style>\n\"\"\", unsafe_allow_html=True)")

new_css = """st.markdown(\"\"\"
<style>
    /* Premium AI SaaS Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, p, h1, h2, h3, h4, h5, h6, div, button, input {
        font-family: 'Inter', sans-serif !important;
    }

    /* AI SaaS Background and Text */
    .stApp {
        background-color: #090C15 !important;
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(59, 130, 246, 0.08), transparent 25%),
            radial-gradient(circle at 85% 30%, rgba(168, 85, 247, 0.08), transparent 25%) !important;
        color: #e2e8f0 !important;
    }

    /* Sidebar Redesign - Workspace Panel */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        min-width: 320px !important;
        max-width: 320px !important;
    }
    
    .sidebar-header {
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        color: #64748b !important;
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Expanders & Accordions */
    .streamlit-expanderHeader {
        border-radius: 12px !important;
        background: rgba(30, 41, 59, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        font-weight: 600 !important;
        color: #e2e8f0 !important;
        padding: 0.75rem 1rem !important;
    }
    .streamlit-expanderContent {
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-top: none !important;
        border-bottom-left-radius: 12px !important;
        border-bottom-right-radius: 12px !important;
        background: rgba(15, 23, 42, 0.5) !important;
    }

    /* Drag & Drop Upload Zone */
    [data-testid="stFileUploadDropzone"] {
        border-radius: 16px !important;
        border: 1.5px dashed rgba(139, 92, 246, 0.3) !important;
        background: rgba(30, 41, 59, 0.3) !important;
        padding: 2rem 1rem !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #a855f7 !important;
        background: rgba(139, 92, 246, 0.05) !important;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.15) !important;
        transform: translateY(-1px) !important;
    }
    [data-testid="stFileUploadDropzone"] svg {
        width: 40px !important;
        height: 40px !important;
        fill: #8b5cf6 !important;
        margin-bottom: 0.5rem !important;
    }
    [data-testid="stFileUploader"] section > button {
        display: none !important; /* Hide default small browse button */
    }

    /* Buttons */
    [data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #4f46e5, #9333ea) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1rem !important;
        box-shadow: 0 4px 15px rgba(147, 51, 234, 0.25) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    [data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(147, 51, 234, 0.4) !important;
    }
    [data-testid="baseButton-secondary"] {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #cbd5e1 !important;
        border-radius: 10px !important;
    }
    [data-testid="baseButton-secondary"]:hover {
        background: rgba(51, 65, 85, 0.8) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
    }

    /* Suggested Prompt Chips */
    div[data-testid="stHorizontalBlock"] button {
        border-radius: 50px !important;
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        color: #94a3b8 !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        white-space: nowrap !important;
    }
    div[data-testid="stHorizontalBlock"] button:hover {
        background: rgba(139, 92, 246, 0.1) !important;
        border-color: #a855f7 !important;
        color: #f8fafc !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(168, 85, 247, 0.2) !important;
    }

    /* Chat Messages */
    .stChatMessage {
        background: transparent !important;
        border: none !important;
        padding: 1rem 0 !important;
        gap: 1.5rem !important;
    }
    [data-testid="chatAvatarIcon-user"] { background-color: #3b82f6 !important; }
    [data-testid="chatAvatarIcon-assistant"] { background: linear-gradient(135deg, #8b5cf6, #d946ef) !important; }

    /* Chat Input Container - Sticky & Glass */
    [data-testid="stChatInput"] {
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 16px !important;
        box-shadow: 0 -10px 40px rgba(11, 15, 25, 0.8) !important;
        padding: 0.5rem !important;
    }
    
    /* Hero Section */
    .hero-container {
        text-align: center;
        padding: 5rem 2rem 3rem 2rem;
        animation: fadeIn 0.8s ease-out;
    }
    .hero-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        display: inline-block;
        filter: drop-shadow(0 0 20px rgba(139, 92, 246, 0.5));
        animation: float 6s ease-in-out infinite;
    }
    .hero-title {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        letter-spacing: -1px;
        margin-bottom: 1rem;
        color: white;
    }
    .gradient-text {
        background: linear-gradient(to right, #60a5fa, #c084fc, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 200% auto;
        animation: gradient 8s linear infinite;
    }
    .hero-subtitle {
        font-size: 1.15rem;
        color: #94a3b8;
        max-width: 600px;
        margin: 0 auto 3rem auto;
        line-height: 1.6;
    }

    /* Animations */
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-15px); }
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Container Spacing */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 6rem !important;
        max-width: 1200px !important;
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin-top: 3rem;
    }
    .stat-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.5rem;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
\"\"\", unsafe_allow_html=True)"""

content = content[:css_start] + new_css + content[css_end:]

# 2. Update the Hero Section
hero_start = content.find("st.markdown(\"\"\"\n<div class=\"hero-container\">")
hero_end = content.find("</p>\n    </div>\n</div>\n\"\"\", unsafe_allow_html=True)") + len("</p>\n    </div>\n</div>\n\"\"\", unsafe_allow_html=True)")

new_hero = """if st.session_state.vector_db is None:
    st.markdown(\"\"\"
    <div class="hero-container">
        <div class="hero-icon">✨</div>
        <h1 class="hero-title">
            <span class="gradient-text">AI Workspace</span>
        </h1>
        <p class="hero-subtitle">
            Your premium AI-powered research platform. Upload documents, extract insights, and perform deep semantic analysis instantly.
        </p>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">⚡</div>
                <div class="stat-label">Fast Search</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">🧠</div>
                <div class="stat-label">Smart RAG</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">📑</div>
                <div class="stat-label">Multi-Doc</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">🔒</div>
                <div class="stat-label">Secure</div>
            </div>
        </div>
    </div>
    \"\"\", unsafe_allow_html=True)"""

content = content[:hero_start] + new_hero + content[hero_end:]

# 3. Update Sidebar layout
sidebar_start = content.find("# Sidebar for controls and uploads\nwith st.sidebar:")
sidebar_end = content.find("st.error(f\"Failed to generate report for download: {e}\")") + len("st.error(f\"Failed to generate report for download: {e}\")")

new_sidebar = """# Sidebar - Workspace Layout
with st.sidebar:
    st.markdown('<div class="sidebar-header">🏢 Workspace</div>', unsafe_allow_html=True)
    
    with st.expander("📂 Document Upload", expanded=True):
        uploaded_files = st.file_uploader(
            "Upload files", 
            type=["pdf", "txt", "docx"], 
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        
        generate_summary = st.checkbox("Generate Executive Summary", value=True)
        
        if st.button("🚀 Process Documents", type="primary"):
            if not uploaded_files:
                st.warning("Please upload at least one document.")
            else:
                st.markdown("**Processing Queue:**")
                for file in uploaded_files:
                    size_mb = file.size / (1024 * 1024)
                    st.markdown(f"📄 **{file.name}** ({size_mb:.2f} MB)")

                import time
                try:
                    with st.status("🧠 AI Processing Pipeline", expanded=True) as status:
                        st.write("⏳ Validating files...")
                        valid_files = validate_uploaded_files(uploaded_files)
                        if not valid_files:
                            status.update(label="❌ Upload failed", state="error")
                            st.stop()
                            
                        st.write("📄 Extracting text...")
                        documents = load_documents(valid_files)
                        st.session_state.raw_documents = documents
                        
                        st.write("✂️ Chunking text...")
                        chunks = chunk_documents(documents)
                        
                        st.write("🔍 Creating BM25 index...")
                        st.session_state.bm25_retriever = BM25Retriever.from_documents(chunks)
                        
                        st.write("🧠 Storing embeddings in Vector DB...")
                        st.session_state.vector_db = embed_documents(chunks)
                        
                        if generate_summary:
                            st.write("📝 Generating executive summary...")
                            st.session_state.executive_summary = generate_executive_summary(documents)
                            
                        status.update(label="✅ Processing Complete!", state="complete", expanded=False)
                    
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Processing error: {e}")
                    logger.error(f"Processing error: {e}")

    if st.session_state.vector_db is not None:
        st.markdown('<div class="sidebar-header">⚙️ Session Controls</div>', unsafe_allow_html=True)
        
        with st.expander("🕒 History & Controls", expanded=False):
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state.messages = []
                st.session_state.langchain_messages = []
                st.rerun()
            if st.button("🔄 Start New Session", use_container_width=True):
                st.session_state.vector_db = None
                st.session_state.bm25_retriever = None
                st.session_state.executive_summary = None
                st.session_state.messages = []
                st.session_state.langchain_messages = []
                st.session_state.raw_documents = []
                st.rerun()

        st.markdown('<div class="sidebar-header">📥 Export</div>', unsafe_allow_html=True)
        with st.expander("💾 Export Session Report", expanded=False):
            if st.session_state.messages or st.session_state.executive_summary:
                format_choice = st.selectbox("Export Format", ["Text File (.txt)"], key="export_format_choice")
                # simplified export logic for space, basic text generation
                report_content = "# RAG Research Report\\n\\n"
                if st.session_state.executive_summary:
                    report_content += "## Executive Summary\\n" + st.session_state.executive_summary + "\\n\\n"
                for msg in st.session_state.messages:
                    report_content += f"### {msg['role']}\\n{msg['content']}\\n\\n"
                    
                st.download_button(
                    label=f"Download Report",
                    data=report_content,
                    file_name="rag_report.txt",
                    mime="text/plain",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.info("No chat history to export yet.")
"""

content = content[:sidebar_start] + new_sidebar + content[sidebar_end:]

with open(app_path, "w", encoding="utf-8") as f:
    f.write(content)
