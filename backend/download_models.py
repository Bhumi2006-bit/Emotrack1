from pathlib import Path
from huggingface_hub import hf_hub_download

BASE = Path(__file__).resolve().parent / "research" / "goemotions_ekman_experiment" / "models_track_b"
REPO_ID = "bhumiasatiiii/emotrack-checkpoints"

files = [
    ("bert_base/best_model.pt", BASE / "bert_base" / "best_model.pt"),
    ("roberta_cnn/best_model.pt", BASE / "roberta_cnn" / "best_model.pt"),
]

for filename, destination in files:
    print(f"Downloading {filename}...")
    hf_hub_download(
        repo_id=REPO_ID,
        filename=filename,
        repo_type="model",
        local_dir=str(BASE),
    )
    if not destination.exists():
        raise FileNotFoundError(f"Download missing: {destination}")
    print(f"Verified: {destination.name} ({destination.stat().st_size / (1024 * 1024):.1f} MB)")

print("Both emotion checkpoints downloaded successfully.")
