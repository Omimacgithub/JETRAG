"""
rag_pipeline.py -- Complete RAG pipeline with LangChain and ChromaDB.

Usage:
    python rag_pipeline.py             # Interactive query mode

Precondition: documents must be indexed and stored on a ChromaDB collection
"""
# External deps: pip install langchain-openai langchain-community langchain-chroma sentence-transformers
from src.backend.config import config
from src.backend.core.vector_store import chroma_client
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from openai import AsyncOpenAI

# --- Configuration ---
CHROMA_DIR = config.CHROMA_PERSIST_DIRECTORY
COLLECTION_NAME = "chest_2"
CHAT_MODEL = config.MODEL_NAME

def get_embedding_model():
    # Query vectors must be produced by the same local model used to index the
    # collection in services/source_service.py (SentenceTransformerEmbeddingFunction).
    return SentenceTransformerEmbeddings(
        model_name=config.EMBEDDINGS_MODEL_PATH,
        model_kwargs={"device": "cuda"},
    )
def load_store():
    """Load existing ChromaDB vector store from disk."""
    return Chroma(
        client=chroma_client,
        collection_name=COLLECTION_NAME,
        #embedding_function=get_embedding_model(),
        #persist_directory=CHROMA_DIR,
    )

def format_docs(docs):
    """Format retrieved documents into a context string."""
    return "\n\n---\n\n".join(
        f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
        for doc in docs
    )


def build_rag_chain(vector_store: Chroma):
    """Assemble the RAG chain: retriever -> prompt -> LLM -> output."""
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": config.TOP_K},
    )


    prompt = ChatPromptTemplate.from_template(
        "You are a helpful assistant. Answer the question based ONLY on "
        "the following context. If the context doesn't contain enough "
        "information, say so.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )

    # model must be sent explicitly: the default ("gpt-3.5-turbo") is rejected by
    # OpenAI-compatible servers with 400 "invalid model ID".
    #aclient = AsyncOpenAI(base_url=config.OPENAI_SERVER_URL,#"http://localhost:8080/v1", 
    #                 api_key=config.API_KEY)

    llm = ChatOpenAI(
        base_url=config.OPENAI_SERVER_URL,
        api_key=config.API_KEY, 
        model=CHAT_MODEL,
        temperature=0,
    )

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    #pdb.set_trace()
    return chain

class RAGLangChain:

    def __init__(self):
        self.chain = build_rag_chain(load_store())
        

    def run_query(self, question):
        
        """Run a query."""
        try:
            return {
                "answer": self.chain.invoke(question),
                "retrieved_documents": []
            }
        except Exception as e:
            print("Error on RAGLangChain: ", e)