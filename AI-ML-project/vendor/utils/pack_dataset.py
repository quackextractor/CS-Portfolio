import os
import shutil
import tempfile
import pandas as pd
from pathlib import Path

def pack_dataset(csv_path: str, output_zip: str):
    """
    Reads the dataset CSV, copies all referenced frames to a temporary directory,
    zips them into a single archive, and cleans up the temporary directory.
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
        print("Zipping archive...")

        # Prepare the output path (shutil.make_archive adds the .zip extension automatically)
        base_name = output_zip
        if base_name.endswith('.zip'):
            base_name = base_name[:-4]

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_zip), exist_ok=True)

        # Create the zip file
        shutil.make_archive(base_name, 'zip', temp_dir)
        print(f"Successfully created zip archive at {base_name}.zip")

    finally:
        # Clean up the temporary directory
        print("Cleaning up temporary directory...")
        shutil.rmtree(temp_dir)
        print("Done.")

if __name__ == "__main__":
    # Fallback for standalone execution
    pack_dataset("data/processed/dataset.csv", "data/processed.zip")