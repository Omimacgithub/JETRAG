from huggingface_hub import snapshot_download

def download_phi3(
    repo_id="microsoft/Phi-3-mini-4k-instruct",
    local_dir="phi3-mini-4k-instruct"
):
    print(f"Downloading {repo_id} to ./{local_dir} ...")
    
    snapshot_download(
        repo_id=repo_id,
        local_dir=local_dir,
        local_dir_use_symlinks=False  # safer for Jetson / ARM systems
    )

    print("Download complete!")

if __name__ == "__main__":
    download_phi3()
