"""
app.py
The core Streamlit frontend entry point.
Why it exists: It provides the intuitive web GUI where a user can perform uploads and trigger RAG workflows.
What breaks without it: The tool remains a headless set of scripts inaccessible to a non-technical end-user.
"""

import streamlit as st
import logging
import tempfile
import os
import shutil
import imageio_ffmpeg
import streamlit.components.v1 as components
import io
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# Automatically bundle ffmpeg into the PATH so the user doesn't have to install it system-wide.
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
ffmpeg_dir = os.path.dirname(ffmpeg_exe)
ffmpeg_alias = os.path.join(ffmpeg_dir, "ffmpeg.exe")

if not os.path.exists(ffmpeg_alias):
    try:
        shutil.copyfile(ffmpeg_exe, ffmpeg_alias)
    except Exception:
        pass

os.environ["PATH"] += os.pathsep + ffmpeg_dir

# Local utils
import config
from utils.validator import validate_uploaded_files
from utils.document_loader import load_documents
from utils.chunker import chunk_documents
from utils.embedder import embed_documents, load_existing_db
from utils.retriever import build_retriever_pipeline
from utils.summarizer import generate_executive_summary
from utils.comparer import generate_comparison
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.retrievers import BM25Retriever

# Voice Integration Utils
from utils.stt import transcribe_audio
from utils.voice_component import voice_recorder_component
import base64

# Configure standard logging to terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Basic Streamlit UI Configuration
st.set_page_config(page_title="RAG Research Assistant", page_icon="📚", layout="wide")

# Inject Adaptive Modern CSS seamlessly integrating with your Streamlit theme (Light or Dark)
st.markdown("""
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
        outline: none !important;
    }
    .streamlit-expanderHeader:focus, .streamlit-expanderHeader:active, .streamlit-expanderHeader:focus-visible {
        outline: none !important;
        border: 1px solid rgba(139, 92, 246, 0.4) !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
    }
    div[data-testid="stExpander"] details:focus, 
    div[data-testid="stExpander"] summary:focus {
        outline: none !important;
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
        padding-left: 60px !important; /* Space for integrated mic on the LEFT */
        padding-right: 10px !important;
    }
    
    [data-testid="stChatInput"] textarea {
        padding-left: 15px !important;
    }
    
    /* Voice Recorder Positioning */
    .stHtmlEmbed {
        background: transparent !important;
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
        max-width: 800px;
        margin: 0 auto 3rem auto;
        line-height: 1.6;
        text-align: center !important;
    }
    .letter-anim {
        opacity: 0;
        display: inline-block;
        animation: letterPulse 4s ease-in-out infinite;
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
    @keyframes letterPulse {
        0%, 100% { opacity: 0; transform: translateY(10px) scale(0.98); }
        15%, 85% { opacity: 1; transform: translateY(0) scale(1); }
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

    /* Stable Positioning for Voice Recorder Mic Icon */
    div.stHtml:has(iframe[src*="voice_recorder"]) {
        position: fixed !important;
        z-index: 10001 !important;
        visibility: hidden !important;
        pointer-events: none !important;
        background: transparent !important;
    }
    div.stHtml:has(iframe[src*="voice_recorder"])[style*="left"] {
        visibility: visible !important;
    }
    div.stHtml:has(iframe[src*="voice_recorder"]) iframe {
        pointer-events: auto !important;
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# Verify API Keys on Startup to catch errors early, but render error in Streamlit
if not config.check_keys():
    st.error("Missing Google API Key! Please configure your .env file before proceeding.")
    st.stop()

# Session state variables
if "vector_db" not in st.session_state:
    st.session_state.vector_db = load_existing_db()
    # If we loaded a vector_db, try to reconstruct BM25 and raw_documents
    if st.session_state.vector_db:
        try:
            data = st.session_state.vector_db.get()
            from langchain_core.documents import Document
            # Reconstruct Document objects from Chroma data
            reconstructed_docs = [
                Document(page_content=doc, metadata=meta) 
                for doc, meta in zip(data['documents'], data['metadatas'])
            ]
            if reconstructed_docs:
                st.session_state.bm25_retriever = BM25Retriever.from_documents(reconstructed_docs)
                # Note: raw_documents is usually the full docs before chunking, 
                # but for session recovery, using chunks is a functional fallback.
                st.session_state.raw_documents = reconstructed_docs 
        except Exception as e:
            logger.warning(f"Could not fully restore session from disk: {e}")
            st.session_state.bm25_retriever = None
            st.session_state.raw_documents = []
    else:
        st.session_state.bm25_retriever = None
        st.session_state.raw_documents = []

if "bm25_retriever" not in st.session_state:
    st.session_state.bm25_retriever = None
if "executive_summary" not in st.session_state:
    st.session_state.executive_summary = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "langchain_messages" not in st.session_state:
    st.session_state.langchain_messages = []
if "raw_documents" not in st.session_state:
    st.session_state.raw_documents = []
if "voice_transcript" not in st.session_state:
    st.session_state.voice_transcript = None
if "voice_key" not in st.session_state:
    st.session_state.voice_key = 0

st.markdown("""
<div class="hero-container">
<div class="hero-icon">✨</div>
<h1 class="hero-title">
<span class="letter-anim" style="animation-delay: 0.00s;">W</span><span class="letter-anim" style="animation-delay: 0.05s;">e</span><span class="letter-anim" style="animation-delay: 0.10s;">l</span><span class="letter-anim" style="animation-delay: 0.15s;">c</span><span class="letter-anim" style="animation-delay: 0.20s;">o</span><span class="letter-anim" style="animation-delay: 0.25s;">m</span><span class="letter-anim" style="animation-delay: 0.30s;">e</span> <span class="letter-anim" style="animation-delay: 0.40s;">t</span><span class="letter-anim" style="animation-delay: 0.45s;">o</span> 
<span class="letter-anim gradient-text" style="animation-delay: 0.55s;">A</span><span class="letter-anim gradient-text" style="animation-delay: 0.60s;">I</span> <span class="letter-anim gradient-text" style="animation-delay: 0.70s;">W</span><span class="letter-anim gradient-text" style="animation-delay: 0.75s;">o</span><span class="letter-anim gradient-text" style="animation-delay: 0.80s;">r</span><span class="letter-anim gradient-text" style="animation-delay: 0.85s;">k</span><span class="letter-anim gradient-text" style="animation-delay: 0.90s;">s</span><span class="letter-anim gradient-text" style="animation-delay: 0.95s;">p</span><span class="letter-anim gradient-text" style="animation-delay: 1.00s;">a</span><span class="letter-anim gradient-text" style="animation-delay: 1.05s;">c</span><span class="letter-anim gradient-text" style="animation-delay: 1.10s;">e</span><span class="letter-anim gradient-text" style="animation-delay: 1.15s;">!</span>
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
""", unsafe_allow_html=True)

# Sidebar - Workspace Layout
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
                        # Clear existing reference and force GC to release file locks on Windows
                        st.session_state.vector_db = None
                        import gc
                        gc.collect()
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




# Main Chat / Query Interface
tab1, tab2 = st.tabs(["💬 Chat Mode", "⚖️ Comparison Mode"])

with tab1:
    if st.session_state.executive_summary:
        with st.expander("📝 Executive Summary of Uploaded Documents", expanded=True):
            st.markdown(st.session_state.executive_summary)

    st.header("💬 Chat with your Documents")

    # Display chat messages from history on app rerun
    chat_container = st.container()
    
    # Container for inputs, pinned to the bottom of the tab relative to chat
    input_container = st.container()
    
    # React to user input
    with input_container:
        suggested_prompt = None
        if st.session_state.vector_db is not None:
            st.markdown("### 💡 Suggested Actions")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("Summarize document", use_container_width=True, key="sq_btn_1"):
                    suggested_prompt = "Summarize document"
            with col2:
                if st.button("Generate report", use_container_width=True, key="sq_btn_2"):
                    suggested_prompt = "Generate report"
            with col3:
                if st.button("Ask questions", use_container_width=True, key="sq_btn_3"):
                    suggested_prompt = "Ask questions"
            with col4:
                if st.button("Extract insights", use_container_width=True, key="sq_btn_4"):
                    suggested_prompt = "Extract insights"
        
        # --- Voice Input Integration ---
        voice_data = voice_recorder_component(key=f"voice_input_{st.session_state.voice_key}")
        
        if voice_data:
            with st.spinner("Transcribing..."):
                try:
                    audio_bytes = base64.b64decode(voice_data)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
                        tmp_audio.write(audio_bytes)
                        tmp_audio_path = tmp_audio.name
                    
                    transcript = transcribe_audio(tmp_audio_path)
                    st.session_state.voice_transcript = transcript
                    os.unlink(tmp_audio_path)
                    st.session_state.voice_key += 1 # Reset component
                    st.rerun()
                except Exception as e:
                    st.error(f"Voice processing error: {e}")
                    st.session_state.voice_key += 1 # Reset even on error

        text_prompt = st.chat_input("Enter your research question...")
        
        # Priority: Voice Transcript > Suggested Prompt > Text Input
        prompt = st.session_state.voice_transcript or suggested_prompt or text_prompt
        
        # Clear voice transcript after use
        if st.session_state.voice_transcript:
            st.session_state.voice_transcript = None
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt:
            # Display user message in chat message container
            st.chat_message("user").markdown(prompt)
            
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.langchain_messages.append(HumanMessage(content=prompt))
            
            if st.session_state.vector_db is None:
                with st.chat_message("assistant"):
                    st.error("Please upload and process documents first before querying.")
            else:
                with st.chat_message("assistant"):
                    try:
                        with st.spinner("Thinking..."):
                            response_dict = build_retriever_pipeline(
                                st.session_state.vector_db,
                                st.session_state.bm25_retriever,
                                prompt, 
                                st.session_state.langchain_messages[:-1] 
                            )
                        
                        # Render Streamed LLM Answer
                        stream_gen = response_dict["stream_generator"]()
                        full_response = st.write_stream(stream_gen)
                        
                        # Render Source Citations
                        sources = response_dict.get("source_documents", [])
                        if sources:
                            st.markdown("**Citations:**")
                            for i, doc in enumerate(sources):
                                with st.expander(f"Source {i+1}: {doc.metadata.get('source', 'Unknown File')}"):
                                    st.write(doc.page_content)
                        else:
                            st.write("*No source documents retrieved.*")
                        
                        # Add assistant response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                        st.session_state.langchain_messages.append(AIMessage(content=full_response))
                            
                    except Exception as e:
                        st.error(f"Failed to fetch an answer. Ensure your API Key is valid. Error: {e}")
                        logger.error(f"Query Error: {e}")

with tab2:
    st.header("⚖️ Multi-Document Comparison")
    st.markdown("Select two or more documents to perform a deep semantic comparison. Our AI will automatically retrieve and re-rank relevant context to generate structured insights.")
    
    if not st.session_state.raw_documents:
        st.info("Please upload and process documents to use the Comparison Mode.")
    else:
        # Get unique document sources
        unique_sources = list(set([doc.metadata.get("source") for doc in st.session_state.raw_documents if doc.metadata.get("source")]))
        
        selected_docs = st.multiselect(
            "Select Documents to Compare",
            options=unique_sources,
            default=unique_sources[:2] if len(unique_sources) >= 2 else unique_sources
        )
        
        if len(selected_docs) < 2:
            st.warning("Please select at least two documents for comparison.")
        else:
            if st.button("Run Deep Comparison", type="primary"):
                with st.spinner("Analyzing, retrieving, and comparing documents..."):
                    try:
                        comparison_result = generate_comparison(
                            selected_docs, 
                            st.session_state.vector_db, 
                            st.session_state.bm25_retriever
                        )
                        
                        if "error" in comparison_result:
                            st.error(comparison_result["error"])
                        else:
                            # Render streamed comparison
                            stream_gen = comparison_result["stream_generator"]()
                            st.write_stream(stream_gen)
                            
                            # Render Source Citations
                            sources = comparison_result.get("source_documents", [])
                            if sources:
                                st.divider()
                                st.markdown("### 📑 Traceability & Sources")
                                st.markdown("The comparison above was generated using the following retrieved context chunks:")
                                for i, doc in enumerate(sources):
                                    with st.expander(f"Source {i+1}: {doc.metadata.get('source', 'Unknown File')}"):
                                        st.write(doc.page_content)
                                        
                    except Exception as e:
                        st.error(f"Failed to generate comparison. Error: {e}")
                        logger.error(f"Comparison Error: {e}")


# Post-Processing Sidebar Updates
with st.sidebar:
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
                import gc
                gc.collect()
                if os.path.exists(config.DB_DIR):
                    try:
                        import chromadb
                        chromadb.api.client.SharedSystemClient.clear_system_cache()
                    except Exception as cache_err:
                        pass
                    
                    try:
                        shutil.rmtree(config.DB_DIR)
                    except Exception as e:
                        st.error(f"Could not delete database folder: {e}")
                st.rerun()
    
        st.markdown('<div class="sidebar-header">📥 Export</div>', unsafe_allow_html=True)
        with st.expander("💾 Export Session Report", expanded=False):
            if st.session_state.messages or st.session_state.executive_summary:
                format_choice = st.selectbox("Export Format", ["Text File (.txt)", "PDF Document (.pdf)"], key="export_format_choice")
                
                report_lines = ["# 📚 Multi-Document RAG Research Report\n"]
                if st.session_state.executive_summary:
                    report_lines.append("## 📝 Executive Summary\n")
                    report_lines.append(st.session_state.executive_summary + "\n\n")
                    
                if st.session_state.messages:
                    report_lines.append("## 💬 Chat History\n")
                    for msg in st.session_state.messages:
                        role = "User Query" if msg["role"] == "user" else "Assistant Response"
                        report_lines.append(f"### {role}\n{msg['content']}\n\n")
                        
                report_content = "\n".join(report_lines)
                
                try:
                    if format_choice == "Text File (.txt)":
                        file_name = "rag_research_report.txt"
                        mime_type = "text/plain"
                        data_to_download = report_content
                    else:
                        file_name = "rag_research_report.pdf"
                        mime_type = "application/pdf"
                        
                        # Initialize PDF with explicit margins
                        pdf = FPDF()
                        pdf.set_margins(20, 20, 20)
                        pdf.add_page()
                        
                        # Set auto page break
                        pdf.set_auto_page_break(auto=True, margin=20)
                        
                        # --- HEADER ---
                        pdf.set_font("helvetica", "B", size=20)
                        pdf.set_text_color(30, 41, 59) # Slate 800
                        pdf.cell(pdf.epw, 15, "Research Intelligence Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
                        
                        pdf.set_font("helvetica", "I", size=9)
                        pdf.set_text_color(100, 116, 139) # Slate 500
                        from datetime import datetime
                        pdf.cell(pdf.epw, 5, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
                        pdf.ln(10)
                        
                        # --- CONTENT ---
                        actual_lines = report_content.splitlines()
                        
                        for line in actual_lines[1:]: # Skip title
                            clean_line = line.strip()
                            
                            if not clean_line:
                                pdf.ln(4)
                                continue
                            
                            if clean_line.startswith("## "):
                                # Section Header (Executive Summary)
                                pdf.ln(5)
                                pdf.set_fill_color(241, 245, 249) # Light blue-gray background
                                pdf.set_font("helvetica", "B", size=14)
                                pdf.set_text_color(37, 99, 235) # Blue 600
                                safe_line = clean_line.replace("## ", "").replace("📝", "").encode('latin-1', 'replace').decode('latin-1')
                                pdf.cell(pdf.epw, 12, f"  {safe_line}", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                                pdf.ln(2)
                                
                            elif clean_line.startswith("### "):
                                # Chat Entry Header (User/Assistant)
                                is_user = "User" in clean_line
                                pdf.ln(4)
                                pdf.set_font("helvetica", "B", size=11)
                                if is_user:
                                    pdf.set_text_color(79, 70, 229) # Indigo 600
                                    label = "USER QUERY"
                                else:
                                    pdf.set_text_color(147, 51, 234) # Purple 600
                                    label = "AI ASSISTANT RESPONSE"
                                
                                pdf.cell(pdf.epw, 8, label, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                                pdf.set_draw_color(226, 232, 240)
                                pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
                                pdf.ln(2)
                                
                            else:
                                # Standard Body Text
                                pdf.set_font("helvetica", size=10)
                                pdf.set_text_color(30, 41, 59)
                                # Clean markdown and weird spacing
                                safe_line = clean_line.replace("**", "").replace("__", "").replace("*", "").replace("_", "").replace("---", "")
                                # Remove common artifacts that break fpdf
                                safe_line = safe_line.encode('latin-1', 'replace').decode('latin-1')
                                pdf.multi_cell(pdf.epw, 6, safe_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                                
                        # --- FOOTER ---
                        # (FPDF handles footer via a class usually, but we'll do a simple loop check or manual add)
                        
                        # Generate PDF bytes
                        data_to_download = bytes(pdf.output())
                    
                    # Force button refresh with a unique key based on format
                    st.download_button(
                        label=f"📥 Download {format_choice.split(' ')[0]} Report",
                        data=data_to_download,
                        file_name=file_name,
                        mime=mime_type,
                        type="primary",
                        use_container_width=True,
                        key=f"dl_btn_v3_{format_choice.replace(' ', '_')}"
                    )
                except Exception as e:
                    st.error(f"Failed to generate report: {e}")
                    # Fallback button for text if PDF fails
                    if format_choice != "Text File (.txt)":
                        st.download_button(
                            label="📥 Download as Text (Fallback)",
                            data=report_content,
                            file_name="report_fallback.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
            else:
                st.info("No chat history to export yet.")
    