#!/bin/bash
# Script para compilar modelos TensorRT para JETRAG
# Requiere: CUDA 12.x, TensorRT 9.x, transformers, torch

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_DIR="$SCRIPT_DIR/models"
TRITON_DIR="$SCRIPT_DIR/triton/models"

mkdir -p "$MODEL_DIR" "$TRITON_DIR"

echo "=== Compilando all-MiniLM-L6-v2 para TensorRT ==="

# Descargar y exportar modelo ONNX
python3 << 'EOF'
from optimum.onnxruntime import ORTModelForFeatureExtraction
from transformers import AutoTokenizer
import os

model_id = "sentence-transformers/all-MiniLM-L6-v2"
save_dir = "./models/minilm-onnx"

print(f"Descargando {model_id}...")
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = ORTModelForFeatureExtraction.from_pretrained(
    model_id,
    export=True,
    provider="CPUExecutionProvider"
)
model.save_pretrained(save_dir)
tokenizer.save_pretrained(save_dir)
print(f"Modelo guardado en {save_dir}")
EOF

# Crear estructura Triton
mkdir -p "$TRITON_DIR/embedding/minilm/1"
cp "$MODEL_DIR/minilm-onnx"/*.onnx "$TRITON_DIR/embedding/minilm/" 2>/dev/null || true

# Crear config.pbtxt para embeddings
cat > "$TRITON_DIR/embedding/minilm/config.pbtxt" << 'EOF'
name: "minilm"
platform: "onnxruntime_onnx"
max_batch_size: 32

input [
  {
    name: "TEXT"
    data_type: TYPE_STRING
    dims: [1]
  }
]

output [
  {
    name: "EMBEDDINGS"
    data_type: TYPE_FP32
    dims: [384]
  }
]

instance_group [
  {
    kind: KIND_GPU
    count: 1
  }
]
EOF

echo "=== Compilando Phi-3-mini para TensorRT-LLM ==="
echo "NOTA: Este paso puede tardar 30-60 minutos dependiendo del hardware"

# Instalar tensorrt_llm si no está
pip install tensorrtllm --upgrade 2>/dev/null || true

# Compilar modelo
python3 << 'EOF'
import subprocess
import os
from huggingface_hub import snapshot_download

model_id = "microsoft/Phi-3-mini-4k-instruct"
model_dir = "./models/phi3-mini"

print(f"Descargando {model_id}...")
snapshot_download(model_id, local_dir=model_dir, ignore_patterns=["*.md", "*.txt"])

print("Convirtiendo a TensorRT-LLM...")
# Este comando compila el modelo (simplificado - ajustar según versión)
cmd = [
    "python3", "-m", "tensorrt_llm.commands.convert",
    "--model_dir", model_dir,
    "--output_dir", "./triton/models/llm/phi3",
    "--dtype", "float16",
    "--tp_size", "1"
]
subprocess.run(cmd, check=True)
print("Conversión completada")
EOF

# Crear config.pbtxt para LLM
mkdir -p "$TRITON_DIR/llm/phi3/1"
cat > "$TRITON_DIR/llm/phi3/config.pbtxt" << 'EOF'
name: "phi3"
platform: "tensorrtllm"
max_batch_size: 1

input [
  {
    name: "PROMPT"
    data_type: TYPE_STRING
    dims: [1]
  },
  {
    name: "MAX_TOKENS"
    data_type: TYPE_INT32
    dims: [1]
  },
  {
    name: "TEMPERATURE"
    data_type: TYPE_FP32
    dims: [1]
  },
  {
    name: "TOP_P"
    data_type: TYPE_FP32
    dims: [1]
  }
]

output [
  {
    name: "GENERATION"
    data_type: TYPE_STRING
    dims: [1]
  }
]

instance_group [
  {
    kind: KIND_GPU
    count: 1
  }
]
EOF

echo "=== Compilación completada ==="
echo "Modelos en: $TRITON_DIR"
