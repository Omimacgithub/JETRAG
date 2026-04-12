import chromadb
from chromadb.config import Settings
from config import settings

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(
    path=settings.CHROMA_PERSIST_DIRECTORY,
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)

def get_or_create_collection(collection_name: str = "jetrag_sources"):
    """Get or create a ChromaDB collection"""
    try:
        collection = chroma_client.get_collection(name=collection_name)
    except:
        collection = chroma_client.create_collection(name=collection_name)
    return collection

def add_embeddings(collection, embeddings, documents, metadatas, ids):
    """Add embeddings to ChromaDB collection"""
    collection.add(
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

def query_collection(collection, query_embeddings, n_results=5, where=None):
    """Query ChromaDB collection"""
    results = collection.query(
        query_embeddings=query_embeddings,
        n_results=n_results,
        where=where
    )
    return results

def delete_from_collection(collection, ids):
    """Delete documents from ChromaDB collection"""
    collection.delete(ids=ids)