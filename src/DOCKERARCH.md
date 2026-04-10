# Esquema de conexión de contenedores Docker
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
│  │                     Volumes (persistentes)               │  │
│  │  ./data/sqlite/jetrag.db    ./data/chroma/               │  │
│  │  ./triton/models/                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

# Fichero docker-compose.yml

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