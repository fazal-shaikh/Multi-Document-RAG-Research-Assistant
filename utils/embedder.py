"""
utils/embedder.py
Converts text chunks into dense vector embeddings using Google Gemini API.
Why it exists: Without embeddings, semantic search is impossible; we could only do exact keyword matches.
What breaks without it: FAISS cannot index string text natively; it requires numerical vectors.
"""

import logging
from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import config

# Set up standard logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Cache the Embeddings model globally to prevent initialization delays
GLOBAL_EMBEDDINGS = None

def get_embeddings():
    global GLOBAL_EMBEDDINGS
    if GLOBAL_EMBEDDINGS is None:
        logger.info(f"Initializing Global Embedding Model ({config.EMBEDDING_MODEL_NAME}) into memory...")
        GLOBAL_EMBEDDINGS = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL_NAME)
    return GLOBAL_EMBEDDINGS

import os
import shutil

def embed_documents(chunks: List[Document]) -> Chroma:
    """
    Takes text chunks and creates a Chroma vector database using Gemini Embeddings,
    persisting it to a local directory.
    
    Args:
        chunks (List[Document]): The chunked documents to be embedded.
        
    Returns:
        Chroma: A Chroma vector store instance containing indexed embeddings.
    """
    try:
        if not chunks:
            raise ValueError("No chunks provided to embed_documents.")
            
        # Clear existing database directory to ensure a fresh session
        if os.path.exists(config.DB_DIR):
            logger.info(f"Attempting to clear existing database at {config.DB_DIR}...")
            
            # Clear Chroma system cache to release file locks
            try:
                import chromadb
                chromadb.api.client.SharedSystemClient.clear_system_cache()
            except Exception as cache_err:
                logger.warning(f"Could not clear chromadb system cache: {cache_err}")

            try:
                shutil.rmtree(config.DB_DIR)
            except Exception as e:
                logger.warning(f"Could not remove directory {config.DB_DIR}: {e}. Attempting to clear contents instead.")
                for filename in os.listdir(config.DB_DIR):
                    file_path = os.path.join(config.DB_DIR, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as res_e:
                        logger.error(f"Failed to delete {file_path}: {res_e}")
            
        # Build and persist the Chroma vector index
        logger.info(f"Creating and persisting Chroma database at {config.DB_DIR}...")
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=get_embeddings(),
            persist_directory=config.DB_DIR
        )
        
        logger.info(f"Chroma vector store successfully created and persisted with {len(chunks)} elements.")
        return vector_store
        
    except ValueError as ve:
        logger.error(f"Value Error during embedding: {ve}")
        raise ve
    except Exception as e:
        logger.error(f"Failed to create/persist embeddings: {e}")
        raise Exception(f"Failed to embed documents. Internal error: {e}")

def load_existing_db() -> Chroma:
    """
    Loads a Chroma vector store from the local persist directory.
    
    Returns:
        Chroma: A Chroma instance if the directory exists, otherwise None.
    """
    if os.path.exists(config.DB_DIR) and os.listdir(config.DB_DIR):
        try:
            logger.info(f"Loading existing database from {config.DB_DIR}...")
            return Chroma(
                persist_directory=config.DB_DIR,
                embedding_function=get_embeddings()
            )
        except Exception as e:
            logger.error(f"Failed to load existing database: {e}")
            return None
    return None
