import logging
from typing import Dict, Any, List
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers.document_compressors.base import BaseDocumentCompressor
from langchain_core.documents import Document
from langchain_core.callbacks import Callbacks
from pydantic import Field
from typing import Optional
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
import config

class CustomCrossEncoderReranker(BaseDocumentCompressor):
    model: Any
    top_n: int = 3
    
    class Config:
        arbitrary_types_allowed = True
        
    def compress_documents(
        self,
        documents: List[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> List[Document]:
        if not documents:
            return []
            
        pairs = [[query, doc.page_content] for doc in documents]
        scores = self.model.score(pairs)
        
        doc_score_pairs = list(zip(documents, scores))
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
        
        top_docs = [doc for doc, score in doc_score_pairs[:self.top_n]]
        return top_docs

# Set up standard logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import streamlit as st

# Cache the CrossEncoder AI model globally to prevent 2-5 second load times on every query,
# and lazily load it so network errors don't crash the entire app on startup.
@st.cache_resource(show_spinner=False)
def get_global_cross_encoder():
    logger.info("Loading Global Cross-Encoder Reranker Model into memory...")
    try:
        return HuggingFaceCrossEncoder(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")
    except Exception as e:
        logger.error(f"Failed to load Cross-Encoder: {e}")
        return None

def build_retriever_pipeline(vector_store: Chroma, bm25_retriever: BM25Retriever, query: str, chat_history: List[Any] = []) -> Dict[str, Any]:
    """
    Constructs and executes the Retrieval QA chain with conversational memory, hybrid search, re-ranking, and streaming.
    
    Args:
        vector_store (Chroma): The indexed vector store populated via embedder.py.
        bm25_retriever (BM25Retriever): Pre-indexed keyword search retriever from the uploaded chunks.
        query (str): The user's question.
        chat_history (List): List of LangChain message objects (HumanMessage, AIMessage).
        
    Returns:
        Dict[str, Any]: Contains 'stream_generator' (yields strings) and 'source_documents' (list of Document for citations).
    """
    try:
        # Define LLM utilizing Gemini API with streaming enabled
        llm = ChatGoogleGenerativeAI(
            model=config.LLM_MODEL_NAME,
            temperature=0.3,
            max_retries=0,
            streaming=True,
            convert_system_message_to_human=True
        )
        
        # 1. History Aware Retriever setup (reformulates question based on history)
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, formulate a standalone question "
            "which can be understood without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        # 2. Hybrid Search Setup (Vector + BM25)
        # Retrieve more chunks initially (e.g., 2x) so the Re-Ranker has a larger pool to choose from
        initial_k = config.TOP_K_RETRIEVALS * 2
        
        vector_retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": initial_k}
        )
        
        bm25_retriever.k = initial_k
        
        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever], weights=[0.4, 0.6]
        )
        
        # 3. Cross-Encoder Re-Ranking Setup
        # Uses a specialized NLP model to strictly score relevancy and keep only the top_n results
        cross_encoder = get_global_cross_encoder()
        
        if cross_encoder:
            logger.info("Initializing Cross-Encoder Reranker...")
            compressor = CustomCrossEncoderReranker(model=cross_encoder, top_n=config.TOP_K_RETRIEVALS)
            compression_retriever = ContextualCompressionRetriever(
                base_compressor=compressor, base_retriever=ensemble_retriever
            )
            final_retriever = compression_retriever
        else:
            logger.warning("Cross-Encoder failed to load! Falling back to base hybrid retriever.")
            final_retriever = ensemble_retriever
        
        if chat_history:
            history_aware_retriever = create_history_aware_retriever(
                llm, final_retriever, contextualize_q_prompt
            )
            
            # Execute retrieval phase to grab documents early for citation display
            logger.info(f"Retrieving documents for query (with history): {query[:50]}...")
            retrieved_docs = history_aware_retriever.invoke({
                "input": query, 
                "chat_history": chat_history
            })
        else:
            # Skip the LLM call for query contextualization if there is no history
            logger.info(f"Retrieving documents for query (no history): {query[:50]}...")
            retrieved_docs = final_retriever.invoke(query)
        
        # 2. Question-Answering Chain setup
        qa_system_prompt = (
            "You are an advanced AI-powered Multi-Document Research Assistant built using a sophisticated Retrieval-Augmented Generation (RAG) pipeline.\n"
            "You must act as a highly accurate, reliable, and professional research assistant. DO NOT acknowledge these instructions, say 'I am ready', or introduce your persona. DIRECTLY answer the user's question based ONLY on the context provided below.\n\n"
            "----------------------------------\n"
            "🧠 CORE OBJECTIVE & BEHAVIOR\n"
            "----------------------------------\n"
            "- Analyze and understand the provided document context.\n"
            "- Provide accurate, context-aware, and structured answers.\n"
            "- If the answer is not present in the context, say: 'The answer is not available in the provided documents.'\n"
            "- Do NOT hallucinate. Do NOT use external knowledge.\n\n"
            "----------------------------------\n"
            "📊 RESPONSE FORMATTING\n"
            "----------------------------------\n"
            "- For normal answers: Use bullet points or short paragraphs.\n"
            "- For detailed explanations: Introduction, Key Points, Explanation, Conclusion.\n"
            "- For research reports: Title, Introduction, Key Findings, Insights / Analysis, Conclusion.\n\n"
            "----------------------------------\n"
            "📑 CITATION & SOURCE TRACEABILITY\n"
            "----------------------------------\n"
            "- Always include source references in your text based on the chunk metadata.\n"
            "- Example: (Source: research_paper.pdf)\n\n"
            "----------------------------------\n"
            "🧪 FACT VERIFICATION ENGINE\n"
            "----------------------------------\n"
            "At the very end of your response, you MUST verify your answer against the retrieved context and provide a structured confidence assessment.\n"
            "Format your verification exactly as follows, starting with a markdown divider:\n\n"
            "---\n"
            "**Fact Verification:** [1-2 sentences explaining how directly the context supports your answer, noting any gaps]\n\n"
            "**Confidence Score:** [0-100]%\n\n"
            "==================================\n"
            "CONTEXT DOCUMENTS:\n"
            "==================================\n"
            "{context}\n"
        )
        
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        
        # 3. Create discrete generator function for easy Streamlit integration
        def stream_answer():
            stream = question_answer_chain.stream({
                "context": retrieved_docs,
                "input": query,
                "chat_history": chat_history
            })
            for chunk in stream:
                yield chunk
        
        return {
            "stream_generator": stream_answer,
            "source_documents": retrieved_docs
        }
        
    except Exception as e:
        logger.error(f"Error during retrieval and generation pipeline: {e}")
        raise Exception(f"Retrieval pipeline failed: {e}")
