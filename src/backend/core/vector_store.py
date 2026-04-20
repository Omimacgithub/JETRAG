import chromadb
from chromadb.config import Settings
from src.backend.config import settings

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(
    path=settings.CHROMA_PERSIST_DIRECTORY,
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True,
        # This solves CORS problem?
        chroma_server_cors_allow_origins=["*"]
    )
)

def get_or_create_collection(embedding_function, collection_name: str = "jetrag_sources"):
    """Get or create a ChromaDB collection"""
    try:
        collection = chroma_client.get_collection(name=collection_name)
    except:
        collection = chroma_client.create_collection(name=collection_name, embedding_function=embedding_function)
    return collection

def add_to_collection(collection, documents, metadatas, ids):
    """Add source to ChromaDB collection"""
    # collection: source set for a chest
    # Embeddings: tensors with relevant features extracted from documents
    # Documents: plain text divided into chunks
    # Metadata: store source id and index of each chunk

    collection.add(
        # ChromaDB compute its own embeddings
        #embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
        ids=ids,
        
    )

def query_collection(collection, embed_flag, query_embeddings, n_results=5, where=None):
    """Query ChromaDB collection"""
    if embed_flag:
        results = collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where
        )
    else:
        results = collection.query(
            query_texts=query_embeddings,
            n_results=n_results,
            where=where
        )   
    return results

def delete_from_collection(collection, ids):
    """Delete documents from ChromaDB collection"""
    collection.delete(ids=ids)