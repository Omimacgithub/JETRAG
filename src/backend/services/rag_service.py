import logging
import time
import asyncio
import pdb
from src.backend.config import config
from typing import List, Tuple, AsyncGenerator
from sqlalchemy.orm import Session
from src.backend.models.source import Source
from src.backend.core.vector_store import get_or_create_collection, query_collection
from llama_cpp import Llama

logger = logging.getLogger(__name__)

if not config.MOCK_MODE:
    llm = Llama(
        model_path=config.GGUF_MODEL,
        n_ctx=config.MAX_TOKENS,
        verbose=False,
        n_gpu_layers=config.GPU_LAYERS,
        n_batch=config.BATCH_SIZE,
        type_k=config.TYPE_K,
        type_v=config.TYPE_V,
        flash_attn=config.FLASH_ATTN,
    )

# Llama class docs: https://llama-cpp-python.readthedocs.io/en/latest/api-reference/#llama_cpp.Llama
print(
    "Built Llama class and loaded "
    + "'"
    + config.GGUF_MODEL.split("/")[-1]
    + "'"
    + " model"
)


def retrieve_relevant_chunks(
    chest_id: int, question: str, top_k: int = config.TOP_K
) -> List[Tuple[str, dict]]:
    """Retrieve relevant chunks for a question from a chest's sources"""
    try:
        # Get embedding for the question (ChromaDB already computes the embedding)

        # Get the collection for this chest
        collection = get_or_create_collection(collection_name=f"chest_{chest_id}")

        # Query the collection
        results = query_collection(
            collection,
            False,
            [question],
            # [question_embedding],  # If you want to provide embeddings
            n_results=top_k,
        )

        # Extract documents and metadata
        documents = results[
            "documents"
        ]  # results.get("documents", [[]])[0] if results.get("documents") else []
        metadatas = results[
            "metadatas"
        ]  # results.get("metadatas", [[]])[0] if results.get("metadatas") else []

        #print("Documents: " + str(documents) + ", Metadatas: " + str(metadatas))
        # Combine documents with their metadata
        if documents == [[]] or metadatas == [[]]:
            return [] 
        relevant_chunks = list(zip(documents, metadatas))

        return relevant_chunks

    except Exception as e:
        logger.error(f"Error retrieving relevant chunks: {e}")
        return []


def filter_sources_by_enabled(
    db: Session, chest_id: int, chunk_metadata_list: List[dict]
) -> List[str]:
    """Filter chunks to only include those from enabled sources"""
    if not chunk_metadata_list:
        return []
    # print("CHUNK METADATA RESULTS: ", str(chunk_metadata_list))

    # Get unique source IDs from metadata
    # REVISIT BELOW CODE LINE FOR DEBUGGING
    source_ids = list(set(meta["source_id"] for meta in chunk_metadata_list))

    if not source_ids:
        return []

    # Get enabled sources for this chest
    enabled_sources = (
        db.query(Source.id)
        .filter(
            Source.chest_id == chest_id,
            Source.is_enabled == True,
            Source.id.in_(source_ids),
        )
        .all()
    )

    enabled_source_ids = [source.id for source in enabled_sources]

    # Filter chunks to only include those from enabled sources
    # filtered_chunks = []
    # for i, meta in enumerate(chunk_metadata_list):
    #   if meta.get("source_id") in enabled_source_ids:
    # We would need to store the actual chunk text somewhere to return it
    # For now, we'll return indices or need to adjust our approach
    #      pass

    # Since we don't have the chunk texts here, we'll need to modify our approach
    # Let's return the metadata for now and adjust the calling function
    return enabled_source_ids  # [meta for meta in chunk_metadata_list if meta["source_id"] in enabled_source_ids]

def get_and_filter_chunks(db, chest_id, question, top_k=5, chunks_collected=[]):
    # 4.1 Compute question embeddings (handled in retrieve_relevant_chunks)
    # 4.2 Vector search
    # 4.3 Retrieve Top-K chunks
    relevant_chunks = retrieve_relevant_chunks(chest_id, question, top_k=top_k)
    print("THE RELEVANT: "+ str(relevant_chunks))
    if not relevant_chunks:
        system_msg = "I couldn't find any relevant information to answer your question."
        if config.STREAMING:
            chunks_collected.append(system_msg)
        return system_msg, None

    # Separate chunks and metadata
    # print("RELEVANT CHUNKSSS: ", relevant_chunks)
    chunk_texts = relevant_chunks[0][0]
    chunk_metadata = relevant_chunks[0][1]
    # print("TEXTS CHUNKSSS: ", chunk_texts)
    # print("METADATA CHUNKSSS: ", chunk_metadata)

    #When evaluating RAG system, we always want all sources enabled
    if not config.EVAL_MODE:
        # 4.4 Filter by enabled sources
        enabled_ids = filter_sources_by_enabled(db, chest_id, chunk_metadata)

        if not enabled_ids:
            system_msg = "I found some information, but it's from disabled sources. Please enable some sources to get an answer."
            if config.STREAMING:
                chunks_collected.append(system_msg)
            return system_msg, None

        # Get the actual chunk texts for filtered metadata
        # We need to match metadata to get the correct chunk texts
        # chunk_metadata example: [{'source_id': 1, 'chunk_index': 0}, {'source_id': 2, 'chunk_index': 0}, {'chunk_index': 1, 'source_id': 3}, {'source_id': 3, 'chunk_index': 0}]
        filtered_chunks = [i for i, x in enumerate(chunk_metadata) if x["source_id"] in enabled_ids]

        return [x for i, x in enumerate(chunk_texts) if i in filtered_chunks], enabled_ids
    else:
        return chunk_texts, chunk_metadata
    """
    filtered_chunks = []
    for meta in enabled_ids:
        # Find the corresponding chunk text
        for i, (chunk_text, chunk_meta) in enumerate(relevant_chunks):
            if chunk_meta == meta:
                filtered_chunks.append(chunk_text)
                break
            """

def format_sse_event(data: str) -> str:
    """Format data as SSE event"""
    return f"data: {data}[ENDLINE]"


def format_sse_done() -> str:
    """Format SSE done event"""
    return "data: [DONE][ENDLINE]"


def store_full_response(
    db: Session, chest_id: int, content: str, sources_used: List[int]
) -> None:
    """Store full assistant response in database"""
    try:
        from src.backend.models.chat_message import ChatMessage as DBChatMessage
        from src.backend.models.schemas import ChatMessageCreate
        assistant_message = ChatMessageCreate(
            role="ASSISTANT",
            content=content,
            sources_used=sources_used,
            chest_id=chest_id,
        )

        db_chat_message = DBChatMessage(**assistant_message.dict())
        db.add(db_chat_message)
        db.commit()
        db.refresh(db_chat_message)
        logger.info(f"Stored streamed response for chest {chest_id}")
    except Exception as e:
        logger.error(f"Error storing streamed response: {e}")


async def rag_answer_async_generator(question: str, context_chunks: List[str], chunks_collected: List[str] = []) -> str:
    """Generate answer using LLM with retrieved context"""
#    if not context_chunks:
        # No context available, answer based on general knowledge
#        prompt = f"""Question: {question}

#Answer the question based on your general knowledge. If you don't know the answer, say so."""
#    else:
        # Combine context chunks
    context = "\n\n".join(context_chunks)
    prompt = f"""Context information is below.
            ---------------------
            {context}
            ---------------------
            Given the context information and not prior knowledge, answer the question.
            Q: {question}
            A:"""
    #print("USER PROMPT: ", prompt)
    if not config.MOCK_MODE:
        output = llm(
            prompt,  # Prompt
            max_tokens=config.MAX_TOKENS,  # 32, # Generate up to 32 tokens, set to None to generate up to the end of the context window
            stream=True,  # Returns a generator object
        )  # Generate a completion, can also call create_completion
        print("PREPARING FOR INFERENCE")
        for item in output:
            text = item["choices"][0]["text"]
            if text:
                chunks_collected.append(text)
                print(f"[{time.time()}] YIELDING CHUNK: {text}")
                yield format_sse_event(text)
    else:
        output = [
                "Hey! ",
                "This ",
                "is ",
                "a ",
                "prebuilt ",
                "response",
                "¿Ustedes ",
                # "¿Ustedes ",
                "piensan ",
                "antes ",
                "de ",
                "hablar ",
                "o ",
                "hablan ",
                "tras ",
                "pensar?\n",
                "**Haré todo**",
                " lo que ",
                "pueda y un ",
                "poco más ",
                "de lo que ",
                "pueda ",
                "si es que ",
                "eso es posible, ",
                "y haré todo ",
                "lo posible ",
                "e incluso lo ",
                "imposible ",
                "si también ",
                "lo imposible ",
                "es posible\n",
                "Hay que ",
                "fabricar ",
                "máquinas ",
                "que nos ",
                "permitan seguir ",
                "fabricando ",
                "máquinas ",
                "porque lo ",
                "que no va a ",
                "hacer nunca la ",
                "máquina es ",
                "fabricar ",
                "**máquinas**",
            ]

    for chunk in output:
        # print(f"[{time.time()}] YIELDING CHUNK: {chunk}")
        await asyncio.sleep(0.1)
        yield format_sse_event(chunk)

    yield format_sse_done()

def rag_answer_generator(question: str, context_chunks: List[str]) -> str:
    """Generate answer using LLM with retrieved context"""
#    if not context_chunks:
        # No context available, answer based on general knowledge
#        prompt = f"""Question: {question}

#Answer the question based on your general knowledge. If you don't know the answer, say so."""
#    else:
        # Combine context chunks
    context = "\n\n".join(context_chunks)
    prompt = f"""Context information is below.
---------------------
{context}
---------------------
Given the context information and not prior knowledge, answer the question.
Q: {question}
A:"""
    #print("USER PROMPT: ", prompt)
    if not config.MOCK_MODE:
        output = llm(
            prompt,  # Prompt
            max_tokens=config.MAX_TOKENS,  # 32, # Generate up to 32 tokens, set to None to generate up to the end of the context window
            stream=False,  # Returns a generator object
        )  # Generate a completion, can also call create_completion
    else:
        output = "Hey! This is a prebuilt response" 
    # This would be an async call in practice
    # For now, we'll return a placeholder
    # for item in output:
    #  yield item['choices'][0]['text']
    # print(item['choices'][0]['text'], end='')
    return output  # f"[RAG Answer Placeholder] Based on the context, here is an answer to: {question}"


def process_rag_query(chest_id: int, question: str, db: Session = None) -> dict:
    """Process a complete RAG query"""
    try:
        # 4.5 Use plain chunks with user query for LLM answer
        enabled_ids = None
        chunk_metadata = None
        if not config.EVAL_MODE:
            chunk_text, enabled_ids = get_and_filter_chunks(db, chest_id, question, top_k=5)
        else: 
            chunk_text, chunk_metadata = get_and_filter_chunks(db, chest_id, question, top_k=5)
        if enabled_ids is None:
            # Not relevant chunks found neither active sources
            return {"answer": chunk_text, "sources_used": []}
        response = rag_answer_generator(question, chunk_text)
        #print("TESTO: ", str(response))
        if not config.EVAL_MODE:
            answer = {"answer": response["choices"][0]["text"], "sources_used": enabled_ids}
                    
            print("Proceeding to message store")
            store_full_response(db, chest_id, answer["answer"], enabled_ids)
            # print("RESPUU: ", answer)

            # Extract source IDs used
            # source_ids_used = list(set(meta.get("source_id") for meta in filtered_metadata if meta.get("source_id")))

            return answer
        else:
            return {"answer": response["choices"][0]["text"], "retrieved_documents": chunk_metadata}

    except Exception as e:
        logger.error(f"Error processing RAG query: {e}")
        return {
            "answer": "Sorry, I encountered an error while processing your question.",
            "sources_used": [],
        }

# You cannot use async keyword when function that streams data for StreamingResponse have blocking functions (example: time.sleep)
async def stream_rag_response(
    db: Session, chest_id: int, question: str
) -> AsyncGenerator[str, None]:
    """Stream RAG response as SSE events"""
    
    try:
        # List to store all yielded chunks when streaming for latter storage
        chunks_collected = []
        context_chunks, enabled_ids = get_and_filter_chunks(db, chest_id, question, top_k=5, chunks_collected=chunks_collected)
        if enabled_ids is None:
            # Not relevant chunks found neither active sources
            yield format_sse_event(context_chunks)
            return
        async for chunk in rag_answer_async_generator(question, context_chunks, chunks_collected=chunks_collected):
            yield chunk
        #print("Proceeding to message store")
        # TODO: we'll deactivate this for the moment
        #system_answer = " ".join(chunks_collected)
        #store_full_response(db, chest_id, system_answer, enabled_ids)
        
    except Exception as e:
        logger.error(f"Error in streaming RAG response: {e}")
        error_chunk = "Sorry, I encountered an error while processing your question."
        yield format_sse_event(error_chunk)
        #TODO: on the future this line may be needed; chunks_collected.append(error_chunk)
