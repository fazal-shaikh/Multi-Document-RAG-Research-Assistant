# 📚 Multi-Document RAG Research Assistant

![RAG Backend](https://img.shields.io/badge/Architecture-RAG-blue)
![LangChain](https://img.shields.io/badge/LangChain-1.13-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red)

A sophisticated end-to-end fullstack Python project implementing Retrieval-Augmented Generation (RAG) using the **Google Gemini API**. Students can upload multi-modal documents (PDF, DOCX, TXT) and instantly interrogate a vast knowledge base.

## 🚀 Features
- **Multi-Document Parsing**: Seamlessly extract data from `.pdf`, `.docx`, and `.txt` utilizing buffered in-memory parsers.
- **Smart Chunking**: Automatic context-length preservation via `RecursiveCharacterTextSplitter`.
- **Vector Search**: Local instance of `FAISS` database powered by Dense Text Embeddings.
- **Citation Engine**: Automatically tracks document lineage and returns explicit citations from source files.

## ⚙️ Quick Start Guide
```bash
# 1. Clone or Download the Repository 
# 2. Setup Virtual Environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate # Mac/Linux

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Environment Variables
cp .env.example .env
# Edit .env and paste your GOOGLE_API_KEY

# 5. Run automated validations checks
python -m pytest test_validation.py

# 6. Launch the App!
streamlit run app.py
```
*Note: Ensure your `.env` contains `GOOGLE_API_KEY="your_api_key"`*

For complete documentation involving IEEE reports, VIVA Questions, and Architectures, refer to `PROJECT_REPORT.md`.
