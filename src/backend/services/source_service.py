import hashlib
import re
from typing import List
from sqlalchemy.orm import Session
from models.source import Source
from models.schemas import SourceCreate, SourceUpdate
from core.vector_store import get_or_create_collection, add_embeddings, delete_from_collection
from core.ml.embeddings import triton_embedding_client
import logging

logger = logging.getLogger(__name__)

def get_source(db: Session, source_id: int):
    return db.query(Source).filter(Source.id == source_id).first()

def get_sources_by_chest(db: Session, chest_id: int, skip: int = 0, limit: int = 100):
    return db.query(Source).filter(Source.chest_id == chest_id).offset(skip).limit(limit).all()

def create_source(db: Session, source: SourceCreate):
    # Generate content hash to avoid re-processing
    content_hash = None
    if source.content:
        content_hash = hashlib.md5(source.content.encode()).hexdigest()
    
    db_source = Source(
        chest_id=source.chest_id,
        name=source.name,
        type=source.type,
        content=source.content,
        content_hash=content_hash,
        is_enabled=source.is_enabled
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    
    # Process the source (chunking, embeddings, storage)
    process_source(db_source, db)
    
    return db_source

def update_source(db: Session, source_id: int, source: SourceUpdate):
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if db_source:
        if source.name is not None:
            db_source.name = source.name
        if source.type is not None:
            db_source.type = source.type
        if source.content is not None:
            db_source.content = source.content
            # Update content hash if content changed
            db_source.content_hash = hashlib.md5(source.content.encode()).hexdigest()
        if source.is_enabled is not None:
            db_source.is_enabled = source.is_enabled
        db.commit()
        db.refresh(db_source)
        
        # Re-process source if content changed
        if source.content is not None:
            process_source(db_source, db)
    
    return db_source

def delete_source(db: Session, source_id: int):
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if db_source:
        # Remove embeddings from ChromaDB
        try:
            collection = get_or_create_collection(f"chest_{db_source.chest_id}")
            # Delete using source ID as part of the document ID
            delete_from_collection(collection, [f"source_{source_id}"])
        except Exception as e:
            logger.warning(f"Could not remove embeddings for source {source_id}: {e}")
        
        db.delete(db_source)
        db.commit()
    return db_source

def process_source(source: Source, db: Session):
    """Process a source: parse, chunk, compute embeddings, store"""
    try:
        # Skip processing if no content or if it's a URL (handled separately)
        if not source.content and source.type != "TXT":
            return
            
        # For URL and FILE types, we would fetch/download content here
        # For simplicity, we'll assume content is already provided for now
        text_content = source.content
        
        if not text_content:
            return
            
        # 3.1 Parse input content (already done - we have text)
        # 3.2 Chunking: Split text on fragments
        chunks = chunk_text(text_content)
        
        if not chunks:
            return
            
        # 3.3 Compute chunk embeddings
        embeddings = triton_embedding_client.embed(chunks)
        
        # 3.4 Store embeddings on ChromaDB along with plain chunks
        collection = get_or_create_collection(f"chest_{source.chest_id}")
        
        # Prepare data for ChromaDB
        documents = chunks
        metadatas = [{"source_id": source.id, "chunk_index": i} for i in range(len(chunks))]
        ids = [f"source_{source.id}_chunk_{i}" for i in range(len(chunks))]
        
        add_embeddings(collection, embeddings, documents, metadatas, ids)
        
        logger.info(f"Processed source {source.id}: {len(chunks)} chunks stored")
        
    except Exception as e:
        logger.error(f"Error processing source {source.id}: {e}")
        raise

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Simple text chunking by sentences with overlap"""
    # Split by sentences (simple regex)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return []
        
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # If adding this sentence would exceed chunk size, store current chunk and start new one
        if len(current_chunk) + len(sentence) + 1 > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Start new chunk with overlap from previous chunk
            words = current_chunk.split()
            overlap_words = words[-overlap//10:] if len(words) > overlap//10 else words
            current_chunk = " ".join(overlap_words) + " " + sentence
        else:
            current_chunk += (" " if current_chunk else "") + sentence
    
    # Add the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
        
    return chunks if chunks else [text]  # Return original text if chunking failed