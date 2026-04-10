# JETRAG

Chatbot RAG local para NVIDIA Jetson con FastAPI, Svelte y ChromaDB.

## Requisitos

- Python 3.11+
- Node.js 20+
- Docker y Docker Compose
- GPU NVIDIA (opcional para desarrollo, necesario para producción)

## Preparación del entorno

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd JETRAG/src
```

### 2. Crear entorno virtual de Python

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno
source venv/bin/activate        # Linux/macOS
# o
.\venv\Scripts\Activate.ps1    # Windows PowerShell
# o
.\venv\Scripts\activate.bat    # Windows CMD

# El prompt mostrará (venv) al inicio
```

### 3. Instalar dependencias del backend

```bash
# Asegúrate de tener el entorno virtual activado
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### 4. Instalar dependencias del frontend

```bash
cd frontend
npm install
cd ..
```

## Desarrollo local

### Sin GPU (mock mode)

Para desarrollo sin GPU, los clientes Triton intentarán conectar a un servidor
externo. Si no está disponible, el servidor FastAPI arrancará pero las
funcionalidades de chat no funcionarán.

```bash
# Backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (en otra terminal)
cd frontend
npm run dev
```

Accede a http://localhost:3000

### Con GPU (Triton local)

1. **Compilar modelos TensorRT** (requiere GPU NVIDIA):

```bash
# Dar permisos al script
chmod +x scripts/build_triton_models.sh

# Ejecutar (puede tardar 30-60 minutos)
./scripts/build_triton_models.sh
```

2. **Iniciar Triton Server**:

```bash
docker run --gpus all -p 8001:8000 -p 8002:8001 -p 8003:8002 \
  -v $(pwd)/triton/models:/models \
  nvcr.io/nvidia/tritonserver:24.01-py3 \
  tritonserver --model-repository=/models --model-control-mode=explicit
```

3. **Iniciar backend y frontend** como en el paso anterior.

## Docker Compose (Producción)

### 1. Crear directorios de datos

```bash
mkdir -p data/sqlite data/chroma
```

### 2. Construir e iniciar

```bash
docker-compose up --build
```

### 3. Acceder

- App: http://localhost:3000
- API: http://localhost:8000
- Triton: http://localhost:8001

## Estructura del proyecto

```
src/
├── backend/              # FastAPI
│   ├── api/routes/      # Endpoints REST
│   ├── core/            # Database, vector store, ML clients
│   ├── models/         # SQLAlchemy + Pydantic
│   └── services/       # Lógica de negocio
├── frontend/           # SvelteKit
│   └── src/
│       ├── lib/components/  # Componentes UI
│       ├── lib/stores/      # Estado reactivo
│       └── routes/          # Páginas
├── scripts/           # Scripts de utilidad
│   └── build_triton_models.sh
└── docker-compose.yml
```

## Troubleshooting

### Error de conexión a Triton

```
Cannot connect to Triton server at http://localhost:8001
```

**Solución**: Verifica que Triton esté corriendo y los modelos estén en
`triton/models/`.

### Error de memoria en Jetson

```
RuntimeError: CUDA out of memory
```

**Solución**: Reduce `max_batch_size` en los config.pbtxt de Triton o usa
modelos más pequeños (Phi-3-mini-q4).

### SQLite permission denied

```bash
chmod 755 data/sqlite
chmod 644 data/sqlite/*.db
```

## API Documentation

Una vez iniciado el backend:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
