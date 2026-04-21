import logging
from src.backend.config import settings
from typing import List, Tuple
from sqlalchemy.orm import Session
from src.backend.models.source import Source
from src.backend.core.vector_store import get_or_create_collection, query_collection
#from src.backend.core.ml.embeddings import triton_embedding_client
#from src.backend.core.ml.llm import triton_llm_client

logger = logging.getLogger(__name__)

def retrieve_relevant_chunks(
    db: Session, 
    chest_id: int, 
    question: str, 
    top_k: int = settings.TOP_K
) -> List[Tuple[str, dict]]:
    """Retrieve relevant chunks for a question from a chest's sources"""
    try:
        # Get embedding for the question (ChromaDB already computes the embedding)
        #question_embedding = triton_embedding_client.embed([question])[0]
        
        # Get the collection for this chest
        collection = get_or_create_collection(collection_name=f"chest_{chest_id}")
        
        # Query the collection
        results = query_collection(
            collection, 
            False,
            [question],
            # [question_embedding],  # If you want to provide embeddings
            n_results=top_k
        )
        
        # Extract documents and metadata
        documents = results["documents"]#results.get("documents", [[]])[0] if results.get("documents") else []
        metadatas = results["metadatas"]#results.get("metadatas", [[]])[0] if results.get("metadatas") else []
        
        # Combine documents with their metadata
        relevant_chunks = zip(documents, metadatas)
        
        return relevant_chunks
        
    except Exception as e:
        logger.error(f"Error retrieving relevant chunks: {e}")
        return []

def filter_sources_by_enabled(db: Session, chest_id: int, chunk_metadata_list: List[dict]) -> List[str]:
    """Filter chunks to only include those from enabled sources"""
    if not chunk_metadata_list:
        return []
    print("CHUNK METADATA RESULTS: ", str(chunk_metadata_list))
        
    # Get unique source IDs from metadata
    # REVISIT BELOW CODE LINE FOR DEBUGGING
    source_ids = list(set(meta["source_id"] for meta in chunk_metadata_list))
    
    if not source_ids:
        return []
        
    # Get enabled sources for this chest
    enabled_sources = db.query(Source.id).filter(
        Source.chest_id == chest_id,
        Source.is_enabled == True,
        Source.id.in_(source_ids)
    ).all()
    
    enabled_source_ids = [source.id for source in enabled_sources]
    
    # Filter chunks to only include those from enabled sources
    filtered_chunks = []
    for i, meta in enumerate(chunk_metadata_list):
        if meta.get("source_id") in enabled_source_ids:
            # We would need to store the actual chunk text somewhere to return it
            # For now, we'll return indices or need to adjust our approach
            pass
    
    # Since we don't have the chunk texts here, we'll need to modify our approach
    # Let's return the metadata for now and adjust the calling function
    return [meta for meta in chunk_metadata_list if meta["source_id"] in enabled_source_ids]

def generate_rag_answer(question: str, context_chunks: List[str]) -> str:
    """Generate answer using LLM with retrieved context"""
    if not context_chunks:
        # No context available, answer based on general knowledge
        prompt = f"""Question: {question}

Answer the question based on your general knowledge. If you don't know the answer, say so."""
    else:
        # Combine context chunks
        context = "\n\n".join(context_chunks)
        prompt = f"""Context information is below.
---------------------
{context}
---------------------
Given the context information and not prior knowledge, answer the question.
Question: {question}
Answer:"""
    
    # Generate answer using Triton LLM
    # LLM INFERENCE CODE HERE!!
    # This would be an async call in practice
    # For now, we'll return a placeholder
    return f"[RAG Answer Placeholder] Based on the context, here is an answer to: {question}"

async def process_rag_query(db: Session, chest_id: int, question: str) -> dict:
    """Process a complete RAG query"""
    try:
        # 4.1 Compute question embeddings (handled in retrieve_relevant_chunks)
        # 4.2 Vector search
        # 4.3 Retrieve Top-K chunks
        relevant_chunks = retrieve_relevant_chunks(db, chest_id, question, top_k=5)
        
        if not relevant_chunks:
            return {
                "answer": "I couldn't find any relevant information to answer your question.",
                "sources_used": []
            }
        
        # Separate chunks and metadata
        #print("RELEVANT CHUNKSSS: ", relevant_chunks)
        chunk_texts = relevant_chunks[0]
        chunk_metadata = relevant_chunks[1]
        #print("METADATA CHUNKSSS: ", chunk_metadata)
        
        # 4.4 Filter by enabled sources
        filtered_metadata = filter_sources_by_enabled(db, chest_id, chunk_metadata)
        
        if not filtered_metadata:
            return {
                "answer": "I found some information, but it's from disabled sources. Please enable some sources to get an answer.",
                "sources_used": []
            }
        
        # Get the actual chunk texts for filtered metadata
        # We need to match metadata to get the correct chunk texts
        filtered_chunks = []
        for meta in filtered_metadata:
            # Find the corresponding chunk text
            for i, (chunk_text, chunk_meta) in enumerate(relevant_chunks):
                if chunk_meta == meta:
                    filtered_chunks.append(chunk_text)
                    break
        
        # 4.5 Use plain chunks with user query for LLM answer
        answer = generate_rag_answer(question, filtered_chunks)
        
        # Extract source IDs used
        #source_ids_used = list(set(meta.get("source_id") for meta in filtered_metadata if meta.get("source_id")))
        
        return {
            "answer": answer,
            "sources_used": filtered_metadata
        }
        
    except Exception as e:
        logger.error(f"Error processing RAG query: {e}")
        return {
            "answer": "Sorry, I encountered an error while processing your question.",
            "sources_used": []
        }