import logging
from typing import List, Any, Dict
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma
from utils.retriever import get_global_cross_encoder, CustomCrossEncoderReranker
import config

logger = logging.getLogger(__name__)

def generate_comparison(selected_sources: List[str], vector_store: Chroma, bm25_retriever: BM25Retriever) -> Dict[str, Any]:
    """
    Retrieves chunks relevant to comparison topics across the selected documents,
    re-ranks them, and generates a structured side-by-side comparison.
    """
    try:
        # 1. Generate broad comparison queries to retrieve semantic concepts
        queries = [
            "What are the main topics and key themes discussed?",
            "What are the similarities and shared concepts between these texts?",
            "What are the primary differences, unique aspects, or conflicting statements?",
            "What are the final conclusions and key insights?"
        ]
        
        all_retrieved_docs = []
        
        # 2. Intelligent Retrieval (Hybrid)
        for q in queries:
            # Vector search
            v_docs = vector_store.similarity_search(q, k=10)
            # BM25 search
            b_docs = bm25_retriever.invoke(q)
            all_retrieved_docs.extend(v_docs + b_docs)
            
        # 3. Filter by selected documents
        filtered_docs = []
        seen_content = set()
        for doc in all_retrieved_docs:
            source = doc.metadata.get("source", "")
            if source in selected_sources and doc.page_content not in seen_content:
                filtered_docs.append(doc)
                seen_content.add(doc.page_content)
                
        if not filtered_docs:
            return {"error": "No relevant content found in the selected documents for comparison."}
            
        # 4. Re-ranking
        logger.info("Re-ranking comparison chunks...")
        cross_encoder = get_global_cross_encoder()
        if cross_encoder:
            compressor = CustomCrossEncoderReranker(model=cross_encoder, top_n=8)
            # We re-rank based on a general comparison prompt
            reranked_docs = compressor.compress_documents(filtered_docs, "Compare similarities, differences, and key insights.")
        else:
            logger.warning("Cross-Encoder failed to load! Falling back to raw hybrid search results.")
            reranked_docs = filtered_docs[:8]
        
        # 5. Generate Comparison using LLM
        llm = ChatGoogleGenerativeAI(
            model=config.LLM_MODEL_NAME,
            temperature=0.2,
            max_retries=2,
            timeout=120.0,
            streaming=True
        )
        
        prompt_template = """
You are an expert AI Research Analyst. Your task is to perform an advanced Multi-Document Comparison.

Compare the following selected documents: {selected_sources}

Using the provided retrieved context chunks from these documents, generate a highly structured, deep comparison report.

Your report MUST include the following sections exactly:

### 📊 Overview
(A brief executive summary of what is being compared. INCLUDE a "Semantic Similarity Percentage" and a "Topic Overlap Score" based on your analysis)

### 🤝 Similarities
(Common topics, shared themes, repeated concepts)

### ⚖️ Differences
(Diverging points, unique aspects of each document)

### ⚠️ Contradictions
(Conflicting statements, inconsistent data, or differing conclusions. If none, state that clearly)

### 💡 Key Insights
(Automatically extracted shared topics, unique topics, and dominant themes)

### 📋 Side-by-Side Comparison
(A markdown table comparing the documents across key topics. Format: | Topic | Document A | Document B | ...)

### 🎯 Final Conclusion
(A concise executive comparison summary)

**RULES:**
1. **Source Traceability:** Every comparison point must include a citation referencing the source document. Format: `[Source: filename.pdf]`
2. **Accuracy:** Base your comparison ONLY on the provided context. Do NOT hallucinate.
3. **Professional Tone:** Feel like an advanced AI research comparison engine.

Context Chunks:
{context}
"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["selected_sources", "context"]
        )
        
        # Format context for prompt
        context_str = ""
        for i, doc in enumerate(reranked_docs):
            context_str += f"\n--- Chunk {i+1} [Source: {doc.metadata.get('source', 'Unknown')}] ---\n"
            context_str += doc.page_content + "\n"
            
        chain = PROMPT | llm
        
        def stream_comparison():
            stream = chain.stream({
                "selected_sources": ", ".join(selected_sources),
                "context": context_str
            })
            for chunk in stream:
                yield chunk.content
                
        return {
            "stream_generator": stream_comparison,
            "source_documents": reranked_docs
        }
    except Exception as e:
        logger.error(f"Error generating comparison: {e}")
        raise Exception(f"Comparison generation failed: {e}")
