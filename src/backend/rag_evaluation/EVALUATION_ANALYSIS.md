# Faithfulness Evaluation Script - Analysis Report

## Files Created

### `src/backend/evaluate_faithfulness.py`
RAG Faithfulness evaluation script that:
- Loads 12 samples from `src/backend/train-00000-of-00001.parquet`
- Generates responses using gemma4 via `http://localhost:8000/v1/` (OpenAI-compatible endpoint)
- Evaluates Faithfulness metric using ragas 0.4.3 with gemma4 as judge LLM
- Uses `ragas.llms.llm_factory` and `ragas.embeddings.OpenAIEmbeddings` (modern ragas APIs)
- Uses raw `openai.OpenAI` client for response generation (to avoid langchain_openai's Pydantic validation)

## Problem Found

**Server returns HTTP 500 on every `/v1/chat/completions` request**, blocking both response generation and ragas judge evaluation.

The server (`llama-cpp-python 0.3.42`) validates its own response with Pydantic before sending it. The response model `ChatCompletionResponseMessage` (defined in `llama_cpp/llama_types.py:109`) has a required `refusal: Optional[str]` field, but the server code that constructs chat responses never populates it, causing Pydantic validation to fail.

## 3 Most Probable Causes

### 1. llama-cpp-python version incompatibility with its own TypedDict models
`llama_types.py:111` declares `refusal: Optional[str]` as a non-optional field in `ChatCompletionResponseMessage` (TypedDict). The server's chat handler in `llama_chat_format.py:523` initializes the response message dict but sets `"refusal": None` only in certain code paths. If the chat formatting path skips this field, Pydantic (v2) rejects the response because the field is required but missing from the dict.

**Fix:** Update llama-cpp-python to the latest version (`pip install --upgrade llama-cpp-python`) or downgrade to a stable release (e.g., `0.3.34`) where this validation bug does not exist.

### 2. Pydantic v2 strict mode enforcing TypedDict field presence
`llama-cpp-python 0.3.42` was installed from source (not PyPI where latest is 0.3.34). This custom build may have been compiled against Pydantic v2 which enforces strict field validation on TypedDict responses. Older Pydantic v1 allowed missing optional fields in TypedDict serialization, but v2 raises a `ValidationError` if a declared-but-Optional field is absent from the output dict.

**Fix:** Either pin Pydantic to v1 (`pip install "pydantic<2"`) or patch the server's response construction to always include `"refusal": None` in the message dict.

### 3. Custom/patched server build missing response field initialization
The process shows `llama_cpp.server` was launched directly (`python3 -m llama_cpp.server`). Version 0.3.42 does not exist on PyPI, indicating a development or custom build. The chat completion handler may have been modified or is a transitional version where the `refusal` field was added to the type definition (`llama_types.py`) but the handler code (`llama_chat_format.py`) was not updated to populate it in all response paths.

**Fix:** Restart the server after upgrading llama-cpp-python to the latest release, or manually patch `/home/omi/.local/lib/python3.10/site-packages/llama_cpp/llama_chat_format.py` to ensure `"refusal": None` is always included in the response message dict.

## Verification Commands

```bash
# Test chat completions (currently fails with 500)
curl -s http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gemma4","messages":[{"role":"user","content":"Say hello"}]}'

# Upgrade llama-cpp-python (recommended fix)
source src/backend/venv/bin/activate
pip install --upgrade llama-cpp-python

# Re-run evaluation after fix
source src/backend/venv/bin/activate
python3 src/backend/evaluate_faithfulness.py
```
