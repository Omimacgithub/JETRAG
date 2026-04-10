from huggingface_hub import snapshot_download

def download_minilm_onnx(
    repo_id="onnx-models/all-MiniLM-L6-v2-onnx",
    local_dir="all-MiniLM-L6-v2-onnx"
):
    print(f"Downloading {repo_id} to ./{local_dir} ...")
    
    snapshot_download(
        repo_id=repo_id,
        local_dir=local_dir,
        local_dir_use_symlinks=False  # safer for Jetson / ARM systems
    )

    print("Download complete!")

if __name__ == "__main__":
    download_minilm_onnx()
