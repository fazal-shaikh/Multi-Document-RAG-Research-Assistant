"""
test_validation.py
Test suite to validate core pipelines of the Multi-Document RAG project.
Run with: pytest test_validation.py
"""

import os
import pytest
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document

import config
from utils.validator import validate_uploaded_files
from utils.chunker import chunk_documents
from utils.embedder import embed_documents

# Mock Streamlit UploadedFile object
class MockUploadedFile:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        
# ---------------------------------------------------------
# Test 1: Imports & Basic Initialization
# ---------------------------------------------------------
def test_imports():
    """Validates that all external dependencies are available."""
    try:
        import streamlit
        import langchain
        import langchain_google_genai
        import google.generativeai
        import pypdf
        import docx
        import chromadb
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

# ---------------------------------------------------------
# Test 2: Configuration Validation
# ---------------------------------------------------------
@patch('os.getenv')
def test_config_check_keys(mock_getenv):
    """Validates check_keys function logic against env missing keys."""
    # Test valid key
    mock_getenv.return_value = "AIzaSy_fake_api_key_valid"
    assert config.check_keys() == True
    
    # Test missing key empty string
    mock_getenv.return_value = ""
    assert config.check_keys() == False
    
    # Test default template key
    mock_getenv.return_value = "your_google_api_key_here"
    assert config.check_keys() == False

# ---------------------------------------------------------
# Test 3: Input Validation Logic (.txt, .pdf supported)
# ---------------------------------------------------------
def test_file_validation():
    """Validates that unsupported files drop silently and securely."""
    valid_file = MockUploadedFile("paper.pdf", 1024)
    invalid_file = MockUploadedFile("malware.exe", 1024)
    another_valid = MockUploadedFile("notes.txt", 500)
    
    files = [valid_file, invalid_file, another_valid]
    validated = validate_uploaded_files(files)
    
    assert len(validated) == 2
    assert "paper.pdf" in [f.name for f in validated]
    assert "notes.txt" in [f.name for f in validated]
    assert "malware.exe" not in [f.name for f in validated]

# ---------------------------------------------------------
# Test 4: Chunking Algorithm Integrity
# ---------------------------------------------------------
def test_chunking_logic():
    """Validates that long documents are actually split."""
    # Create string > chunk size (1000 characters)
    long_text = "A" * 2500
    doc = Document(page_content=long_text, metadata={"source": "test.txt"})
    
    # Override chunk config for robust test scaling
    config.CHUNK_SIZE = 1000
    config.CHUNK_OVERLAP = 100
    
    chunks = chunk_documents([doc])
    
    # 2500 len / 900 effective advance roughly = 3 chunks
    assert len(chunks) >= 2
    assert chunks[0].page_content.startswith("A" * 10)
    assert chunks[0].metadata["source"] == "test.txt"

# ---------------------------------------------------------
# Test 5: End-to-End Mocked Embedding
# ---------------------------------------------------------
@patch('utils.embedder.get_embeddings')
@patch('utils.embedder.Chroma.from_documents')
def test_embedding_pipeline(mock_chroma, mock_embeddings):
    """Validates entire embedding trigger mechanism without hitting expensive real APIs."""
    mock_chroma.return_value = MagicMock(name="Chroma_DB")
    
    docs = [Document(page_content="Mock test chunk", metadata={"source": "test"})]
    result = embed_documents(docs)
    
    mock_embeddings.assert_called_once()
    mock_chroma.assert_called_once()
    assert result is not None
