"""
utils/chunker.py
Splits massive text documents into properly sized chunks using LangChain text splitters.
Why it exists: LLMs have token context limits. Sending entire books in one API call will fail.
What breaks without it: Pushing raw documents directly to an embedder or LLM triggers Max Token Errors.
"""

import logging
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import config

# Set up standard logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Splits a list of full LangChain Documents into overlapping smaller chunks.
    
    Args:
        documents (List[Document]): The entire original loaded documents list.
        
    Returns:
        List[Document]: New list of document fragments ready to be vectorized.
        
    Example:
        >>> chunks = chunk_documents(raw_docs)
    """
    try:
        # Initialize text splitter adhering to config-defined window params
        # Overlap preserves contextual coherence midway through sentences between chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        # Split original docs into much smaller docs, retaining source metadata
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Successfully chunked {len(documents)} docs into {len(chunks)} chunks.")
        return chunks
        
    except ValueError as ve:
        # Common error if config sizes are improperly set (e.g. negative integers)
        logger.error(f"Configuration value error during text split: {ve}")
        return []
    except Exception as e:
        # Generic exceptions thrown by internal Langchain functions
        logger.error(f"Failed to chunk documents due to an unknown issue: {e}")
        return []
