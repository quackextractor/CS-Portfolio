"""
setup_models.py - Download required MediaPipe model files.

Model URLs and destinations are sourced from config.yaml (models.downloads).

Run this once after installing dependencies:
    python setup_models.py
    # or via the unified CLI:
    python main.py setup
"""
import os
import yaml
import urllib.request

CONFIG_PATH = "config.yaml"


def _load_models(config_path: str = CONFIG_PATH) -> list:
    """Read the models.downloads list from config.yaml."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config.get("models", {}).get("downloads", [])


def download_models(config_path: str = CONFIG_PATH) -> None:
    models = _load_models(config_path)
    if not models:
        print("No models configured in config.yaml under models.downloads.")
        return

    os.makedirs("models", exist_ok=True)

    for m in models:
        dest = m["dest"]
        if os.path.isfile(dest):
            print(f"Already exists, skipping: {dest}")
            continue
        print(f"Downloading {m['description']}...")
        try:
            urllib.request.urlretrieve(m["url"], dest)
            print(f"  Saved to {dest}")
        except Exception as e:
            print(f"  ERROR downloading {m['url']}: {e}")
            raise

    print("All models ready.")


if __name__ == "__main__":
    download_models()
