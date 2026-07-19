"""
config.py
This file centralizes configuration, constants, and environment variables.
Why it exists: Prevents hardcoded values scattered throughout the codebase, making maintenance easier.
What breaks without it: App will fail due to missing API keys or invalid component settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Prevent HuggingFace Transformers from attempting to load TensorFlow (which crashes due to a protobuf version conflict)
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

# ==========================================
# SYSTEM CONSTANTS
# ==========================================
# Embedding Model (HuggingFace local model choice)
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
# Language Model (Gemini LLM choice)
LLM_MODEL_NAME = "gemini-2.5-flash"

# Chunking Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval Configuration
TOP_K_RETRIEVALS = 5

# Supported file types
SUPPORTED_FILE_TYPES = [".pdf", ".txt", ".docx"]

# Database Configuration
DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db_v2")

# ==========================================
# VALIDATION LOGIC
# ==========================================
def check_keys() -> bool:
    """
    Validates the presence of required API keys in the environment.

    Returns:
        bool: True if all required keys are present, False otherwise.
    
    Example:
        >>> check_keys()
        True
    """
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key or google_api_key.strip() == "" or google_api_key.strip() == "your_google_api_key_here":
        return False
    return True
