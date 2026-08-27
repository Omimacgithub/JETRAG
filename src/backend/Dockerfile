# Set base image matching Python 3.10
FROM python:3.10-slim

# First of all
RUN echo "alias ls='ls --color=auto'" >> /root/.bashrc

# Set environment variables for clean Python execution
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/src/backend

# Copy requirements file first to leverage Docker layer caching
# TODO: Need to distinguish device arch
COPY requirements_test.txt constraints_x86.txt .

# Add sentence_transformers package
RUN echo "sentence_transformers" >> /app/src/backend/requirements_test.txt

# Install dependencies (matches 'Install dependencies' step)
RUN python3 -m pip install --no-cache-dir -r requirements_test.txt -c constraints_x86.txt

# Copy the rest of the application code
COPY config.py main.py .

COPY api api/ 

COPY core core/

COPY models models/

COPY services services/ 

COPY tests tests/

# For test execution
COPY ../../pyproject.toml /app

# Install compilers to build llama_cpp_python

RUN apt update && apt install -y \
    build-essential \
    cuda-nvcc-13-3 \
    cublas-cuda-13 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Add llama_cpp_python package
#RUN echo "llama_cpp_python" >> /app/src/backend/requirements_test.txt
#RUN CMAKE_ARGS="-DGGML_CUDA=on" python3 -m pip install --no-cache-dir -r requirements_test.txt -c constraints_x86.txt

CMD ["python3"]