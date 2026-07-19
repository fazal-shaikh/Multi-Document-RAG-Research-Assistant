"""
utils/validator.py
Functions to validate user uploads (types, sizes, etc.).
Why it exists: Prevents unsupported or malicious files from breaking the document loader.
What breaks without it: Corrupted files could crash the entire application unnoticed.
"""

import os
import logging
from typing import List, Any
import config

# Set up logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def validate_uploaded_files(uploaded_files: List[Any]) -> List[Any]:
    """
    Validates a list of Streamlit UploadedFile objects against supported formats.
    
    Args:
        uploaded_files (List[Any]): List of files uploaded by the user via Streamlit.
        
    Returns:
        List[Any]: A filtered list containing only valid files.
        
    Example:
        >>> valid_files = validate_uploaded_files([file1, file2])
    """
    valid_files = []
    
    if not uploaded_files:
        return valid_files
    
    # Iterate through all uploaded files to validate each
    for file in uploaded_files:
        try:
            # Extract file extension to verify format
            _, ext = os.path.splitext(file.name)
            ext = ext.lower()
            
            # Verify if extension exists in config.SUPPORTED_FILE_TYPES
            if ext in config.SUPPORTED_FILE_TYPES:
                # File is valid, add to list
                valid_files.append(file)
                logger.info(f"File {file.name} validated successfully.")
            else:
                # Known but unsupported format
                logger.warning(f"File {file.name} ignored: Unsupported type {ext}.")
                print(f"File {file.name} skipped: {ext} not in {config.SUPPORTED_FILE_TYPES}")
        
        except AttributeError as e:
            # Catch file objects that don't have a 'name' attribute
            logger.error(f"Validation failed (Missing name attribute): {e}")
        except Exception as e:
            # Catch general validation errors without crashing
            logger.error(f"Unexpected validation error for {file}: {e}")
            
    return valid_files
