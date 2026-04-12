# JETRAG - Local RAG Chatbot Application

JETRAG is a web application that allows users to interact with a Retrieval-Augmented Generation (RAG) chatbot using "chests" (collections of source information like plain text, URLs, or files). The application runs completely locally for enhanced security, especially when dealing with sensitive documents.

## Software Requirements

### Local Development
- **Node.js**: v16 or higher
- **Python**: 3.8 or higher
- **Git**: For version control
- **Docker**: For containerized deployment (optional for local development)
- **NVIDIA GPU**: Required for Triton inference server (CPU fallback available but slower)

### Docker Deployment
- Docker Engine v20.10+
- Docker Compose v2.0+
- NVIDIA Container Toolkit (for GPU acceleration)
- Minimum 8GB RAM recommended

## Local Development Setup

### Backend (FastAPI)

1. Clone the repository:
```bash
git clone <repository-url>
cd JETRAG
```

2. Create and activate Python virtual environment:
```bash
# Create venv
python3 -m venv venv

# Activate venv
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

3. Install backend dependencies:
```bash
pip install -r requirements.txt
```

5. Start the backend server:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (SvelteKit)

1. Install frontend dependencies:
```bash
cd frontend
# Generate package-lock.json
npm install
# Clean install
npm ci
```

2. Start the development server:
```bash
npm run dev
```

3. The frontend will be available at http://localhost:3000

## Docker Deployment

### Prerequisites
1. Install NVIDIA Container Toolkit:
   ```bash
   # Add the package repositories
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   
   sudo apt-get update
   sudo apt-get install -y nvidia-docker2
   sudo systemctl restart docker
   ```

2. Pull required Triton models (you'll need to provide your own models):
   ```bash
   # Create model directories
   mkdir -p triton/models/phi3/1
   mkdir -p triton/models/all-MiniLM-L6-v2/1
   
   # Place your TensorRT-LLM Phi-3 model in triton/models/phi3/1/
   # Place your Triton all-MiniLM-L6-v2 model in triton/models/all-MiniLM-L6-v2/1/
   
   # Create model config files (config.pbtxt) in each model directory
   ```

### Deployment Steps

1. Build and start the containers:
```bash
docker-compose up --build
```

2. The application will be available at:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

3. To stop the containers:
```bash
docker-compose down
```

## Service URLs

When running locally:
- **Frontend (SvelteKit)**: http://localhost:3000
- **Backend (FastAPI)**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Triton Inference Server**: http://localhost:8001 (internal to Docker network)

When running with Docker Compose:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Backend internal services**: Accessible via Docker network

## Persistent Volumes

The application uses Docker volumes for data persistence:
- `./data/sqlite/jetrag.db`: SQLite database containing chests, sources, and chat messages
- `./data/chroma/`: ChromaDB vector database for storing embeddings
- `./triton/models/`: Directory for TensorRT-optimized models (read-only)

## Configuration

Environment variables can be configured in a `.env` file at the project root:
```
# Database
DATABASE_URL=sqlite:///./data/sqlite/jetrag.db

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./data/chroma

# Triton
TRITON_SERVER_URL=http://triton:8001
TRITON_LLM_MODEL_NAME=phi3
TRITON_EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2

# API
API_V1_STR=/api
PROJECT_NAME=JETRAG
```

## Development Notes

### Backend
- The backend uses FastAPI with SQLAlchemy ORM for SQLite
- ML inference is handled via NVIDIA Triton Inference Server
- Embedding model: all-MiniLM-L6-v2
- Language model: Phi-3-mini-4k-instruct
- Vector database: ChromaDB

### Frontend
- Built with SvelteKit and TypeScript
- State management using Svelte stores
- Styling with TailwindCSS (via CDN)
- Component-based architecture

### Model Requirements
For full GPU acceleration, you need to provide:
1. TensorRT-LLM optimized Phi-3-mini-4k-instruct model
2. Triton server compatible all-MiniLM-L6-v2 embedding model

Refer to NVIDIA's documentation for converting models to TensorRT-LLM format.

## Troubleshooting

### Common Issues

1. **Triton Connection Errors**:
   - Ensure Triton server is running and accessible
   - Check that model repository is correctly configured
   - Verify GPU visibility in container (`nvidia-smi` inside container)

2. **Database Connection Issues**:
   - Verify SQLite file permissions in `./data/sqlite/`
   - Check that the directory exists and is writable

3. **Frontend Proxy Issues**:
   - Ensure frontend is configured to proxy API requests to backend
   - Check CORS settings in backend if developing locally without proxy

4. **Memory Constraints**:
   - On systems with limited memory, consider reducing batch sizes
   - Monitor memory usage during embedding generation

## License

This project is proprietary software. All rights reserved.

## Support

For issues or questions, please refer to the documentation or contact the development team.
