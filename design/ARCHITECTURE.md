# JETRAG - Arquitectura Técnica

## 1. Stack Tecnológico

### Backend & RAG

| Componente | Tecnología | Justificación |
|------------|------------|----------------|
| **RAG Framework** | **LlamaIndex** | Más ligero que LangChain (~40% menos overhead), mejor integración con Triton y vectordbs embebidos. API más intuitiva para casos de uso RAG específicos. |
| **Backend Framework** | **FastAPI** | Asíncrono por defecto, tipado estático, overhead mínimo vs Flask. Ideal para inferencia de ML con streaming de respuestas. |
| **ORM** | **SQLAlchemy + SQLite** | SQLite es zero-config y consume ~0MB en idle. SQLAlchemy proporciona abstracción sin overhead excesivo. |

### Modelos de ML

| Componente | Modelo | Justificación |
|------------|--------|----------------|
| **LLM Chat** | **Phi-3-mini-4k-instruct** (3.8B params) | Diseñado para dispositivos edge, ~2GB en Q4. Rendimiento comparable a modelos 7B. Soporte nativo ONNX/TensorRT. |
| **Embeddings** | **all-MiniLM-L6-v2** (22M params) | ~90MB, 384 dim, Latency 0.24ms/inference. Optimizado para sentence similarity, 6x más rápido que ada-002. |
| **Inference Engine** | **NVIDIA Triton + TensorRT-LLM** | Cuantización INT8/FP16 nativa, batching dinámico, KV cache optimizado. Reduce VRAM ~50% vs inference naive. |

### Database

| Tipo | Tecnología | Justificación |
|------|------------|----------------|
| **Vector Store** | **ChromaDB** (embebido) | DB de vectores ligera embebida en SQLite, gestión de colecciones, filtering por metadata. Alternativa: FAISS para máximo control pero más código. |
| **Document Store** | **SQLite** (ficheros locales) | Almacenamiento de contenido raw + metadatos. Sin overhead de servidor. |

### Frontend

| Componente | Tecnología | Justificación |
|------------|------------|----------------|
| **Framework** | **Svelte + SvelteKit** | Bundle <50KB vs React ~150KB, reactivity sin virtual DOM, mejor memory footprint. Ideal para SPAs ligeras. |
| **Styling** | **TailwindCSS** (CDN/ JIT) | Zero runtime CSS, purge automático. Reduce CSS final a ~10KB. |
| **State** | **Svelte stores** | Nativo de Svelte, zero overhead. |

### Infrastructure

| Componente | Tecnología | Justificación |
|------------|------------|----------------|
| **Container Runtime** | **Docker + BuildKit** | Multi-arch builds (AMD64/ARM64), layer caching, multi-stage builds para minimal footprint. |
| **Orchestration** | **Docker Compose** | Suficiente para 1 usuario, sin overhead de Kubernetes. |

---

## 2. Estructura de Carpetas

```
jetrag/
├── docker-compose.yml              # Orquestación de servicios
├── Dockerfile                      # Imagen base ARM64
├── .env.example                    # Variables de entorno
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
│   │   │   ├── sources.py         # CRUD fuentes
│   │   │   └── chat.py            # Streaming chat endpoint
│   │   └── dependencies.py         # Inyección de dependencias
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py             # SQLite + SQLAlchemy session
│   │   ├── vector_store.py         # ChromaDB wrapper
│   │   └── ml/
│   │       ├── __init__.py
│   │       ├── llm.py              # Triton client (LLM)
│   │       └── embeddings.py      # Triton client (Embeddings)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chest.py                # Modelo SQLAlchemy: Chest
│   │   ├── source.py               # Modelo SQLAlchemy: Source
│   │   └── schemas.py              # Pydantic schemas
│   └── services/
│       ├── __init__.py
│       ├── chest_service.py        # Lógica de cofres
│       ├── source_service.py       # Lógica de fuentes (parsers)
│       └── rag_service.py         # Pipeline RAG (query + retrieve + generate)
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

---

## 3. Modelo de Datos

### Entidades Principales

```
┌─────────────────────┐       ┌─────────────────────┐
│        Chest        │       │       Source        │
├─────────────────────┤       ├─────────────────────┤
│ id: UUID (PK)       │──┐    │ id: UUID (PK)       │
│ name: String        │  │    │ chest_id: UUID (FK) │──┐
│ created_at: DateTime│  │    │ name: String        │  │
│ updated_at: DateTime│  └───►│ type: Enum(TXT,URL, │  │
│                     │       │        FILE)        │  │
│                     │       │ content: Text      │  │
│                     │       │ content_hash: String│  │
│                     │       │ is_enabled: Boolean │  │
│                     │       │ embedding_id: String │  │
│                     │       │ created_at: DateTime │  │
│                     │       └─────────────────────┘  │
│                     │                               │
│                     │       ┌─────────────────────┐  │
│                     │       │   ChatMessage       │  │
│                     │       ├─────────────────────┤  │
│                     │       │ id: UUID (PK)       │  │
│                     │       │ chest_id: UUID (FK)│  │
│                     │       │ role: Enum(USER,   │  │
│                     │       │        ASSISTANT)  │  │
│                     │       │ content: Text       │  │
│                     │       │ sources: JSON       │  │
│                     │       │ created_at: DateTime│  │
│                     │       └─────────────────────┘  │
└─────────────────────┘                               │
                                                     │
      ┌──────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│          ChromaDB Collections        │
├─────────────────────────────────────┤
│ Collection: chest_{id}              │
│                                     │
│ Document {                          │
│   id: source_id,                   │
│   embedding: float[384],            │
│   document: text_chunk,             │
│   metadata: {                       │
│     source_id,                      │
│     chunk_index,                    │
│     source_name                     │
│   }                                 │
│ }                                   │
└─────────────────────────────────────┘
```

### Esquema SQL (SQLite)

```sql
-- Tabla de cofres
CREATE TABLE chests (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de fuentes
CREATE TABLE sources (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    chest_id TEXT NOT NULL REFERENCES chests(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('TXT', 'URL', 'FILE')),
    content TEXT,                          -- Contenido raw o URL
    content_hash TEXT,                     -- Para evitar re-procesar
    is_enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de mensajes del chat
CREATE TABLE chat_messages (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    chest_id TEXT NOT NULL REFERENCES chests(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK(role IN ('USER', 'ASSISTANT')),
    content TEXT NOT NULL,
    sources_used JSON,                     -- Lista de sources utilizados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_sources_chest ON sources(chest_id);
CREATE INDEX idx_messages_chest ON chat_messages(chest_id);
```

---

## 4. Diagrama de Flujo

### Flujo Principal: Crear Cofre y Chatear

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              USUARIO                                           │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  PASO 1: Página Principal (MAIN view)                                         │
│  ─────────────────────────────────                                           │
│  Usuario ve lista de cofres existentes                                        │
│  └─► Acciones: Ver detalle / Crear nuevo / Eliminar                          │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
          ┌─────────────────────────┴─────────────────────────┐
          │                                                   │
          ▼                                                   ▼
┌─────────────────────┐                         ┌─────────────────────┐
│  Crear nuevo cofre  │                         │  Seleccionar cofre  │
│  (sin fuentes)      │                         │                     │
└──────────┬──────────┘                         └──────────┬──────────┘
           │                                              │
           └────────────────────┬─────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  PASO 2: Chat View (CHAT view)                                               │
│  ─────────────────────────────────                                           │
│  Panel lateral (izq): Gestión de fuentes                                     │
│  Área principal: Chat con el LLM                                             │
└──────────────────────────────────────────────────────────────────────────────┘
                                │
          ┌─────────────────────┴─────────────────────┐
          │                                           │
          ▼                                           ▼
┌─────────────────────┐                 ┌─────────────────────┐
│  Añadir fuente      │                 │  Enviar mensaje     │
│  (TXT/URL/FILE)     │                 │  al chat            │
└──────────┬──────────┘                 └──────────┬──────────┘
           │                                      │
           ▼                                      │
┌─────────────────────────────────────┐          │
│  PASO 3: Procesamiento de fuente    │          │
│  ─────────────────────────────────  │          │
│  3.1 Parsear contenido              │          │
│      └─► Extraer texto              │          │
│  3.2 Chunking (RecursiveCharacter)  │          │
│      └─► Split en fragments        │          │
│  3.3 Generar embeddings            │          │
│      └─► Triton → all-MiniLM-L6    │          │
│  3.4 Almacenar en ChromaDB          │          │
│      └─► Colección: chest_{id}     │          │
│  3.5 Guardar metadata en SQLite     │          │
└─────────────────────────────────────┘          │
                                                  ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  PASO 4: Pipeline RAG (al enviar mensaje)                                    │
│  ────────────────────────────────────                                       │
│                                                                              │
│    Usuario pregunta                                                          │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │ Retrieve (RAG)  │───►│   Augment       │───►│   Generate      │         │
│  │                 │    │                 │    │                 │         │
│  │ 4.1 Query emb   │    │ 4.2 Build ctx   │    │ 4.3 LLM prompt  │         │
│  │    └─► Triton   │    │    └─► System   │    │    └─► Triton   │         │
│  │ 4.3 Vector search│    │       + User   │    │    + streaming  │         │
│  │    └─► ChromaDB │    │       + Context │    │    + sources    │         │
│  │ 4.4 Top-K chunks│    │ 4.4 Inject refs │    │                 │         │
│  │ 4.5 Filter by   │    └─────────────────┘    └─────────────────┘         │
│  │      enabled    │                                                    │
│  │      sources    │                                                    │
│  └─────────────────┘                                                    │
└──────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  PASO 5: Renderizar respuesta                                                │
│  ───────────────────────────                                                 │
│  Streaming del texto → Mostrar en burbuja de chat                            │
│  Referencias a fuentes → Citas clickeables                                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Flujo: Añadir Fuente

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Usuario  │────►│ Selector │────►│ Parser   │────►│ Chunking │
│ selecciona│    │ de tipo  │     │ contenido│     │          │
└──────────┘     └──────────┘     └──────────┘     └────┬─────┘
                             │                          │
         ┌───────────────────┼──────────────────────────┘
         │                   │                   
         ▼                   ▼                   ▼
    ┌─────────┐         ┌─────────┐         ┌─────────┐
    │   TXT   │         │   URL   │         │  FILE   │
    │ (paste) │         │ (fetch) │         │ (upload)│
    └────┬────┘         └────┬────┘         └────┬────┘
         │                   │                   │
         └───────────────────┴───────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Embedding gen  │
                    │  (Triton/MiniLM)│
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ ChromaDB insert │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ SQLite metadata │
                    └─────────────────┘
```

---

## 5. Decisiones de Diseño

### 1. LlamaIndex sobre LangChain
**Decisión**: Usar LlamaIndex como framework RAG principal.

**Justificación**: 
- **Memory footprint**: LangChain tiene overhead de ~200MB por sus chains abstractions. LlamaIndex es más modular y permite cargar solo los componentes necesarios.
- **Integración Triton**: LlamaIndex tiene drivers nativos para Triton Inference Server (`TritonEmbedding`, `TritonLLM`), mientras que LangChain requiere adaptadores custom.
- **Vector stores**: Soporte first-class para ChromaDB, FAISS, con query engines optimizados.
- **Debugging**: Query engines permiten visualizar el retrieval pipeline, crítico para debugging en edge.

### 2. Phi-3-mini como LLM
**Decisión**: Usar Microsoft Phi-3-mini-4k-instruct (3.8B params) cuantizado a Q4.

**Justificación**:
- **RAM constraint**: 8GB total. Un modelo 7B en Q4 usa ~4.5GB VRAM + overhead. Phi-3-mini en Q4 usa ~2.2GB, dejando espacio para embeddings + sistema operativo.
- **Performance**: En benchmarks MMLU supera a Llama-2-7B-chat despite being 50% smaller.
- **Edge-optimized**: Diseñado para dispositivos constrained. Soporte INT8/FP16 nativo.
- **Contexto**: 4K tokens es suficiente para RAG donde el contexto relevante se limita a chunks retrieved.

### 3. ChromaDB embebido con SQLite
**Decisión**: Usar ChromaDB (embebido) + SQLite para metadata.

**Justificación**:
- **Zero-ops**: No requiere servidor separado. ChromaDB embebido usa SQLite internamente.
- **Filtrado por metadata**: Los chest tienen collections separadas, permitiendo filtrado natural por `source_id`.
- **Simplicidad operacional**: Un solo proceso Python, sin dependencias externas.
- **Alternativa descartada**: Qdrant requiere servicio separado (~100MB RAM overhead).

### 4. Streaming responses con Server-Sent Events (SSE)
**Decisión**: Implementar streaming de respuestas del LLM via SSE en lugar de polling/websockets.

**Justificación**:
- **Eficiencia de red**: Tokens llegan en tiempo real, mejor UX percibida.
- **Simplicidad**: WebSockets son overkill para unidireccional. SSE usa HTTP/1.1 standard.
- **Compatibilidad**: Funciona con proxy reversos (nginx/caddy) sin configuración especial.
- **Reconnection**: Browsers manejan reconexiones automáticamente.

### 5. Svelte sobre React
**Decisión**: Frontend con Svelte (no SvelteKit para la SPA) para maximizar ligereza.

**Justificación**:
- **Bundle size**: React + ReactDOM = ~150KB minified. Svelte compilado = ~10KB.
- **Memory**: React usa virtual DOM con ~2x overhead de memoria para estado. Svelte compile-time reactivity.
- **Mantenibilidad**: Sintaxis declarativa similar a Vue/React, curva de aprendizaje baja.
- **Docker**: Imagen frontend más pequeña (~20MB vs ~150MB para Node Alpine + React).

---

## 6. Riesgos Técnicos

### Riesgo 1: OOM (Out of Memory) durante inferencia
**Descripción**: Con 8GB RAM total, cargar LLM (2.2GB) + embeddings (90MB) + ChromaDB + SQLite + OS + Docker puede agotar memoria, especialmente con batch requests o contextos largos.

**Probabilidad**: Alta (3/5) - Escenario real bajo carga.

**Mitigación**:
```yaml
# docker-compose.yml - Límites de memoria
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 4G        # Reservar 4GB para inference
        reservations:
          memory: 2G
    environment:
      - PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
      - TORCHinductor.enabled=false  # Evita allocations grandes
```

**Implementación adicional**:
- Streaming de respuestas para no mantener contexto completo en memoria
- Chunking lazy: no cargar todos los embeddings de golpe
- Monitor de memoria (`psutil`) que rechaza requests si RAM > 85%
- TensorRT con memory pool size limitado

---

### Riesgo 2: Latencia de inferencia inaceptable
**Descripción**: Phi-3-mini en Jetson puede tomar 15-30 segundos por respuesta debido a:
- JIT compilation de TensorRT en primera inference
- Memory bandwidth limitado en Jetson Nano/Orin NX
- No batching optimizado para queries single-user

**Probabilidad**: Media (2/5)

**Mitigación**:
1. **Pre-warm del modelo**: Cargar modelo en startup, no bajo demanda
2. **KV cache optimizado**: Triton maneja esto, pero verificar config:
   ```python
   # tensorrt_llm config
   enable_multi_block_mode: true  # Mejora batching implícito
   enable_remove_input_padding: true
   ```
3. **Quantización agresiva**: Usar INT8 en lugar de FP16 si quality lo permite
4. **Cache de embeddings**: Sources no cambian frecuentemente. Cachear embeddings en ChromaDB.
5. **Prefetch de context**: Cuando user está escribiendo, hacer pre-compute de query embedding

---

### Riesgo 3: Gestión de Ficheros Locales (File Upload)
**Descripción**: Subir archivos grandes (>10MB) puede:
- Bloquear el event loop de FastAPI
- Exceder límites de memoria
- Crear inconsistencias si el proceso muere

**Probabilidad**: Media (2/5) - Si se soporta PDF/DOCs con parsing.

**Mitigación**:
```python
# Endpoints con streaming de archivos
from fastapi import UploadFile, File
import aiofiles

@router.post("/sources/upload")
async def upload_file(
    chest_id: str,
    file: UploadFile = File(...)
):
    # Límites
    if file.size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(413, "File too large")
    
    # Stream a disco
    path = f"/data/uploads/{uuid4()}_{file.filename}"
    async with aiofiles.open(path, 'wb') as f:
        while chunk := await file.read(64 * 1024):
            await f.write(chunk)
    
    # Background processing (no bloquear request)
    await process_file_background(chest_id, path)
    return {"status": "processing", "path": path}
```

**Parsers lazy**:
- PDF: `pdfminer.six` con streaming page-by-page
- DOCX: `python-docx` con parsing lazy
- No procesar todo en memoria

---

## 7. Configuración Recomendada para Jetson

### Jetson Orin NX 8GB

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    build: ./backend
    runtime: nvidia
    environment:
      NVIDIA_VISIBLE_DEVICES: all
      CUDA_VISIBLE_DEVICES: "0"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
        limits:
          memory: 6G
    volumes:
      - ./data:/app/data
      - ./triton:/app/triton:ro  # Modelos pre-compilados
    command: uvicorn main:app --host 0.0.0.0 --port 8000

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

### Pre-compilación de Modelos TensorRT

```bash
# scripts/build_triton_engines.sh
#!/bin/bash
# Pre-compilar modelos para Jetson (ARM64 + CUDA)

# Phi-3-mini Q4
python3 -m tensorrt_llm.commands.build \
  --model_dir ./models/phi3-mini-4k-instruct \
  --quantization fp8 \
  --gemm_plugin auto \
  --output_dir ./triton/llm/phi3/engine \
  --max_batch_size 1 \
  --max_input_len 4096 \
  --max_output_len 512

# MiniLM embeddings
trtexec --onnx=./models/minilm.onnx \
  --saveEngine=./triton/embedding/minilm.engine \
  --fp16
```

---

## 8. API Endpoints

### Chests
```
GET    /api/chests                    # Listar todos
POST   /api/chests                    # Crear cofre
GET    /api/chests/{id}               # Detalle cofre
PATCH  /api/chests/{id}               # Actualizar nombre
DELETE /api/chests/{id}               # Eliminar cofre
```

### Sources
```
GET    /api/chests/{id}/sources       # Listar fuentes
POST   /api/chests/{id}/sources       # Crear fuente
  Body: { type: "TXT", content: "..." }
  Body: { type: "URL", url: "https://..." }
  Body: { type: "FILE", file_id: "uuid" }
DELETE /api/sources/{id}              # Eliminar fuente
PATCH  /api/sources/{id}              # Toggle enabled
```

### Chat
```
POST   /api/chests/{id}/chat          # Enviar mensaje (streaming SSE)
  Body: { message: "..." }
  Response: text/event-stream

GET    /api/chests/{id}/messages      # Historial de chat
```

---

## 9. Flujo de Dependencias Docker

```
┌─────────────────────────────────────────────────────────────────┐
│                        docker-compose                           │
│                                                                 │
│  ┌─────────────────┐                    ┌─────────────────────┐ │
│  │    frontend     │                    │      backend        │ │
│  │  (SvelteKit)    │◄──── REST ────────►│     (FastAPI)       │ │
│  │   Port: 3000    │                    │    Port: 8000       │ │
│  │                 │                    │                     │ │
│  │   - Static      │                    │  ┌───────────────┐ │ │
│  │   - No DB       │                    │  │  LlamaIndex   │ │ │
│  │                 │                    │  ├───────────────┤ │ │
│  └─────────────────┘                    │  │   Triton      │ │ │
│                                         │  │   Client      │ │ │
│                                         │  └───────┬───────┘ │ │
│                                         └──────────┼──────────┘ │
│                                                    │            │
│                                         ┌──────────▼──────────┐ │
│                                         │    NVIDIA Triton     │ │
│                                         │    Server            │ │
│                                         │    (GPU Inference)   │ │
│                                         │                      │ │
│                                         │  ┌───────────────┐   │ │
│                                         │  │   Phi-3-mini  │   │ │
│                                         │  │   (Q4/INT8)   │   │ │
│                                         │  ├───────────────┤   │ │
│                                         │  │   MiniLM-L6   │   │ │
│                                         │  │   (FP16)     │   │ │
│                                         │  └───────────────┘   │ │
│                                         └──────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     Volumes (persistentes)                │  │
│  │  ./data/sqlite/jetrag.db    ./data/chroma/               │  │
│  │  ./data/uploads/             ./triton/models/            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```