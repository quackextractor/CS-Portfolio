import os
import shutil
import tempfile
import pandas as pd
import zipfile
from pathlib import Path

def pack_dataset(csv_path: str, output_zip: str):
    """
    Reads the dataset CSV, copies all referenced frames to a temporary directory,
    zips them into a single archive (uncompressed for speed), and cleans up.
    """
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    print(f"Reading dataset from {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    if 'filepath' not in df.columns:
        print("Error: 'filepath' column not found in the CSV.")
        return

    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="dataset_pack_")
    print(f"Created temporary directory: {temp_dir}")

    try:
        count = 0
        missing = 0
        
        # Copy files to temp directory
        for filepath in df['filepath']:
            filepath = str(filepath)
            if os.path.exists(filepath):
                # Preserve the directory structure inside the temp folder
                dest_path = os.path.join(temp_dir, filepath)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(filepath, dest_path)
                count += 1
            else:
                missing += 1

        print(f"Copied {count} files to temporary folder. Missing files: {missing}.")
        print("Zipping archive (Store Mode)...")

        # Prepare the output path
        base_name = output_zip
        if not base_name.endswith('.zip'):
            base_name = f"{base_name}.zip"

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(base_name), exist_ok=True)

        # Create the zip file without applying extra compression
        with zipfile.ZipFile(base_name, 'w', zipfile.ZIP_STORED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Keep the internal folder structure clean
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
                    
        print(f"Successfully created zip archive at {base_name}")

    finally:
        # Clean up the temporary directory
        print("Cleaning up temporary directory...")
        shutil.rmtree(temp_dir)
        print("Done.")

if __name__ == "__main__":
    # Fallback for standalone execution
    pack_dataset("data/processed/dataset.csv", "data/processed.zip")