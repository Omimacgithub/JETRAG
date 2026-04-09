# Árbol de ficheros (la raíz es este directorio)

```
├── docker-compose.yml              # Orquestación de servicios
├── Dockerfile                      # Imagen base ARM64
├── .env                            # Variables de entorno
│
├── backend/                        # Servicio FastAPI
│   ├── __init__.py
│   ├── main.py                     # Entry point, CORS, lifespan
│   ├── config.py                   # Settings con pydantic
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── chests.py           # CRUD cofres
│   │   │   ├── sources.py          # CRUD fuentes
│   │   │   └── chat.py             # Streaming chat endpoint
│   │   └── dependencies.py         # Inyección de dependencias
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
│   │   ├── chest.py                # Modelo SQLAlchemy: Chest
│   │   ├── source.py               # Modelo SQLAlchemy: Source
│   │   └── schemas.py              # Pydantic schemas
│   └── services/
│       ├── __init__.py
│       ├── chest_service.py        # Lógica de cofres
│       ├── source_service.py       # Lógica de fuentes (parsers)
│       └── rag_service.py          # Pipeline RAG (query + retrieve + generate)
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
│   │       ├── +page.svelte        # Lista de cofres (MAIN)
│   │       └── chest/
│   │           └── [id]/
│   │               └── +page.svelte  # Chat view (CHAT)
│   └── static/
│
├── triton/                         # Model repository (volumen Docker)
│   ├── llm/
│   │   └── phi3/                   # TensorRT-LLM engine
│   │       ├── config.pbtxt
│   │       └── 1/
│   └── embedding/
│       └── minilm/
│           ├── config.pbtxt
│           └── 1/
│
├── data/                           # Volumen persistente
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