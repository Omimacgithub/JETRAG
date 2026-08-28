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
RUN echo "\nsentence_transformers" >> /app/src/backend/requirements_test.txt

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
#COPY ../../pyproject.toml /app/

# Install tools compilers to build llama_cpp_python

RUN apt update && apt install -y \
    build-essential \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://developer.download.nvidia.com/compute/cuda/repos/debian13/$(arch)/cuda-keyring_1.1-1_all.deb

RUN dpkg -i cuda-keyring_1.1-1_all.deb

# Install cuda stuff

RUN apt update && apt install -y \
    cuda-nvcc-13-3 \
    cublas-cuda-13 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Build llama_cpp_python package
#RUN CMAKE_ARGS="-DGGML_CUDA=on" python3 -m pip install --no-cache-dir -r requirements.txt -c constraints_x86.txt

CMD ["python3"]