# Esquema SQL (SQLite)

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