FROM ghcr.io/omimacgithub/jetrag/src/backend

# Set environment variables for clean Python execution
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/src/backend

RUN CMAKE_ARGS="-DGGML_CUDA=on" python3 -m pip install --no-cache-dir -r requirements.txt -c constraints_x86.txt

WORKDIR /app

CMD ["python3", "-m", "uvicorn", "src.backend.main:app", "--host 0.0.0.0", "--port 8000", "--reload"]