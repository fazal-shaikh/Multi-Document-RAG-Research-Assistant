import logging
from typing import List
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def generate_executive_summary(documents: List[Document]) -> str:
    """
    Generates an executive summary of the uploaded documents.
    Takes a combined string of the front-parts of the texts to avoid hitting token limits
    and asks the LLM to provide a structured overview.
    """
    try:
        if not documents:
            return "No documents provided for summarization."
            
        # Extract text, limit to first 30,000 characters to keep it snappy and within limits
        combined_text = "\n\n".join([doc.page_content for doc in documents])
        truncated_text = combined_text[:30000]
        
        llm = ChatGoogleGenerativeAI(
            model=config.LLM_MODEL_NAME,
            temperature=0.2,
            max_retries=0
        )
        
        prompt_template = """
        You are an expert Research Analyst. Please provide a concise, high-level Executive Summary 
        of the following document(s). 
        
        Provide the summary in the following format:
        - **Core Topic:** What is this document primarily about?
        - **Key Themes:** Bullet points of 3-4 main themes discussed.
        - **Brief Overview:** A 2-3 sentence summary of the contents.
        
        Document Content:
        {text}
        """
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["text"]
        )
        
        logger.info("Generating executive summary...")
        chain = PROMPT | llm
        
        response = chain.invoke({"text": truncated_text})
        return response.content
        
    except Exception as e:
        error_msg = str(e).lower()
        if "429" in error_msg or "quota" in error_msg or "rate limit" in error_msg:
            logger.error("Rate limit exceeded while drafting executive summary.")
            return "⚠️ Executive summary could not be generated because your Google API Key has reached its quota/rate limit. Please check your Google AI Studio billing or limits."
            
        logger.error(f"Error generating executive summary: {e}")
        return f"Could not generate summary due to an error: {str(e)}"
