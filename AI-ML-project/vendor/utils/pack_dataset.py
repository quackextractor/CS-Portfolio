import os
import pandas as pd
import zipfile
from pathlib import Path

def pack_dataset(csv_path: str, output_zip: str):
    """
    Reads the dataset CSV and writes all referenced frames directly into an
    uncompressed zip archive, bypassing the slow temporary copy phase.
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

    # Prepare the output path
    base_name = output_zip
    if not base_name.endswith('.zip'):
        base_name = f"{base_name}.zip"

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(base_name), exist_ok=True)

    print("Packing files directly to archive (Store Mode)...")
    count = 0
    missing = 0

    # Write directly to the zip file, skipping the temp folder entirely
    with zipfile.ZipFile(base_name, 'w', zipfile.ZIP_STORED) as zipf:
        for filepath in df['filepath']:
            filepath_str = str(filepath)
            
            if os.path.exists(filepath_str):
                path_obj = Path(filepath_str)
                
                try:
                    # Find 'processed' in the path and set it as the root for the archive
                    processed_idx = path_obj.parts.index('processed')
                    arcname = os.path.join(*path_obj.parts[processed_idx:])
                except ValueError:
                    # Fallback if 'processed' is somehow not in the filepath
                    arcname = filepath_str
                
                zipf.write(filepath_str, arcname)
                count += 1
            else:
                missing += 1

    print(f"Packed {count} files. Missing files: {missing}.")
    print(f"Successfully created zip archive at {base_name}")

if __name__ == "__main__":
    # Fallback for standalone execution
    pack_dataset("data/processed/dataset.csv", "data/processed.zip")