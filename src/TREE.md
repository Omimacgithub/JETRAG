# Tree file structure

```
├── docker-compose.yml              
├── Dockerfile                      # ARM64 image
├── .env                            
│
├── backend/                        # FastAPI
│   ├── __init__.py
│   ├── main.py                     # Entry point, CORS, lifespan
│   ├── config.py                   # Settings with pydantic
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── chests.py           # chests CRUD 
│   │   │   ├── sources.py          # sources CRUD
│   │   │   └── chat.py             # Streaming chat endpoint
│   │   └── dependencies.py         # Dependency injection
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py             # SQLite + SQLAlchemy session
│   │   ├── vector_store.py         # ChromaDB wrapper
│   │   └── ml/
│   │       ├── __init__.py
│   │       ├── llm.py              # Triton client (LLM)
│   │       └── embeddings.py       # Triton client (Embeddings)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chest.py                # SQLAlchemy model: Chest
│   │   ├── source.py               # SQLAlchemy model: Source
│   │   └── schemas.py              # Pydantic schemas
│   └── services/
│       ├── __init__.py
│       ├── chest_service.py        # chest logic
│       ├── source_service.py       # sources logic (parsers)
│       └── rag_service.py          # RAG pipeline
│
├── frontend/                       # SvelteKit app
│   ├── package.json
│   ├── svelte.config.js
│   ├── vite.config.js
│   ├── src/
│   │   ├── app.html
│   │   ├── app.css                 # Tailwind base
│   │   ├── lib/
│   │   │   ├── components/
│   │   │   │   ├── ChestList.svelte
│   │   │   │   ├── ChestCard.svelte
│   │   │   │   ├── SourcePanel.svelte
│   │   │   │   ├── SourceWidget.svelte
│   │   │   │   ├── ChatArea.svelte
│   │   │   │   ├── MessageBubble.svelte
│   │   │   │   └── AddSourceModal.svelte
│   │   │   ├── stores/
│   │   │   │   ├── chests.ts
│   │   │   │   └── chat.ts
│   │   │   └── api/
│   │   │       └── client.ts       # API client wrapper
│   │   └── routes/
│   │       ├── +layout.svelte
│   │       ├── +page.svelte        # Chests list (CHESTS PAGE)
│   │       └── chest/
│   │           └── [id]/
│   │               └── +page.svelte  # Chat view (CHAT PAGE)
│   └── static/
│
├── triton/                         # Model repository (Docker volume)
│   ├── llm/
│   │   └── phi3/                   # TensorRT-LLM engine
│   │       ├── config.pbtxt
│   │       └── 1/
│   └── embedding/
│       └── minilm/
│           ├── config.pbtxt
│           └── 1/
│
├── data/                           # Persistent volume
│   ├── sqlite/
│   │   └── jetrag.db
│   └── chroma/
│       └── (ChromaDB files)
│
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_api/
    ├── test_services/
    └── test_integration/
```