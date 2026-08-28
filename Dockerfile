FROM ghcr.io/omimacgithub/jetrag/src/backend:latest

# Set environment variables for clean Python execution
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH" \
    LD_LIBRARY_PATH="/usr/local/cuda/targets/x86_64-linux/include/:/usr/local/lib/python3.10/site-packages/nvidia/cu13/include/:$LD_LIBRARY_PATH" \
    CPLUS_INCLUDE_PATH="/usr/local/cuda/targets/x86_64-linux/include/:/usr/local/lib/python3.10/site-packages/nvidia/cu13/include/$CPLUS_INCLUDE_PATH" \
    LIBRARY_PATH="/usr/local/cuda/targets/x86_64-linux/include/:/usr/local/lib/python3.10/site-packages/nvidia/cu13/include/:$LIBRARY_PATH" \
    CXX_INCLUDE_PATH="/usr/local/cuda/targets/x86_64-linux/include/:/usr/local/lib/python3.10/site-packages/nvidia/cu13/include/:$CXX_INCLUDE_PATH" \
    C_INCLUDE_PATH="/usr/local/cuda/targets/x86_64-linux/include/:/usr/local/lib/python3.10/site-packages/nvidia/cu13/include/:$C_INCLUDE_PATH" \
    CMAKE_CUDA_COMPILER="/usr/local/cuda/bin"

WORKDIR /app/src/backend

RUN CMAKE_CUDA_COMPILER="/usr/local/cuda/bin" CMAKE_ARGS="-DGGML_CUDA=on" python3 -m pip install --no-cache-dir -r requirements.txt -c constraints_x86.txt

WORKDIR /app

CMD ["python3", "-m", "uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
