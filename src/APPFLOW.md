```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                 USER                                         │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: CHESTS PAGE (Starting page)                                         │
│  ─────────────────────────────────                                           │
│  User see list of created chests and button to create new ones               │
│  └─► Actions: See chest details / Create new chest / Delete chest            │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
          ┌─────────────────────────┴─────────────────────────┐
          │                                                   │
          ▼                                                   ▼
┌─────────────────────┐                         ┌─────────────────────┐
│  Create new chest   │                         │  See chest details  │
│  (Empty set of sources)      │                │                     │
└──────────┬──────────┘                         └─────────┬──────────┘
           │                                              │
           └────────────────────┬─────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: CHAT PAGE                                                           │
│  ─────────────────────────────────                                           │
│  Left panel: Chest information sources management                            │
│  Main area: Chatbot                                                          │ 
|  Top right corner: create new chest                                          │
└──────────────────────────────────────────────────────────────────────────────┘
                                │
          ┌─────────────────────┴─────────────────────┬──────────────────────────────┐
          │                                           │                              │
          ▼                                           ▼                              ▼
┌─────────────────────┐                 ┌─────────────────────┐           ┌─────────────────────┐ 
│  (Left panel) add source │            │  (Main area) Send   │           │  Create new chest   │
│  (TXT/URL/FILE)     │                 │  message to chatbot │           │  (Empty set of sources)      │
└──────────┬──────────┘                 └────────┬────────────┘           └──────────┬──────────┘
           │                                     │                                   ▼
           ▼                                     │                         ┌─────────────────────┐
┌─────────────────────────────────────┐          │                         │  GO BACK TO STEP 2  │
│  STEP 3: Source processing          │          │                         └─────────────────────┘
│  ─────────────────────────────────  │          │
│  3.1 Parse input content            │          │
│      └─► Extract text               │          │
│  3.2 Chunking                       │          │
│      └─► Split text on fragments    │          │
│  3.3 Compute chunk embeddings       │          │
│      └─► Triton → all-MiniLM-L6     │          │
│  3.4 Store embeddings on ChromaDB   │          │
│   along with plain chunks           │          │
│      └─► Add to chest db model      │          │
│  3.5 Store metadata on SQLite       │          │
│  3.6 Go back to step 2 with new sources│       │
└─────────────────────────────────────┘          │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: RAG PIPELINE (when messages are sent)                                          │
│  ────────────────────────────────────                                                   │
│                                                                                         │
│    User asks                                                                            │
│         │                                                                               │
│         ▼                                                                               │
│  ┌──────────────────────────────────┐                                                   │
│  │ RAG                              │                                                   │
│  │                                  │                                                   │
│  │ 4.1 Compute question embeddings  │                                                   │
│  │    └─► Triton                    │                                                   │
│  │ 4.2 Vector search                │                                                   │
│  │    └─► ChromaDB                  │                                                   │
│  │ 4.3 Retrieve Top-K chunks        │                                                   │
│  │ 4.4 Filter by enabled sources    │                                                   │
│  │ 4.5 Use plain chunks with        │                                                   │
│   │ user query for LLM answer        │                                                   │
│  │                                  │                                                   │
│  └──────────────────────────────────┘                                                   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 5: Answer rendering                                                    │
│  ───────────────────────────                                                 │
│  Text streaming → Display inside bubble on chat                              │
│  Source refs → Clickable cites                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```