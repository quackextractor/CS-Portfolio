import os
import glob
from collections import defaultdict
from pathlib import Path
import pandas as pd


def get_dir_stats(directory):
    """Calculates count and total size in MB of files in a directory (recursively)."""
    all_files = []
    total_size = 0
    
    if not os.path.exists(directory):
        return 0, 0, []

    for root, _, files in os.walk(directory):
        for f in files:
            # Match any file with an extension
            if "." in f:
                f_path = os.path.join(root, f)
                all_files.append(f_path)
                total_size += os.path.getsize(f_path)
    
    count = len(all_files)
    total_size_mb = total_size / (1024 * 1024)
    return count, total_size_mb, all_files


def get_source_name(file_path, base_dir):
    """
    Determines the source name (subfolder or video name) from the file path.
    """
    try:
        rel_path = os.path.relpath(file_path, base_dir)
        parts = Path(rel_path).parts
        if len(parts) > 1:
            # It is in a subfolder, use the subfolder name as the source
            return parts[0]
        return "root"
    except ValueError:
        return "unknown"


def print_status(config):
    raw_pos_dir = config.get("data", {}).get("raw_positive_dir", "data/raw/positive")
    raw_neg_dir = config.get("data", {}).get("raw_negative_dir", "data/raw/negative")
    processed_dir = config.get("data", {}).get("processed_dir", "data/processed")
    proc_pos_dir = os.path.join(processed_dir, "positive")
    proc_neg_dir = os.path.join(processed_dir, "negative")

    raw_pos_count, raw_pos_size, raw_pos_files = get_dir_stats(raw_pos_dir)
    raw_neg_count, raw_neg_size, raw_neg_files = get_dir_stats(raw_neg_dir)
    proc_pos_count, proc_pos_size, proc_pos_files = get_dir_stats(proc_pos_dir)
    proc_neg_count, proc_neg_size, proc_neg_files = get_dir_stats(proc_neg_dir)

    print("\n" + "="*60)
    print("DIRECTORY STATISTICS")
    print("="*60)
    print(f"RAW TARGET (1):    {raw_pos_count:>5} frames  ({raw_pos_size:>7.2f} MB)")
    print(f"RAW RANDOM (0):    {raw_neg_count:>5} frames  ({raw_neg_size:>7.2f} MB)")
    print(f"PROC TARGET (1):   {proc_pos_count:>5} frames  ({proc_pos_size:>7.2f} MB)")
    print(f"PROC RANDOM (0):   {proc_neg_count:>5} frames  ({proc_neg_size:>7.2f} MB)")

    # Calculations
    total_raw = raw_pos_count + raw_neg_count
    total_proc = proc_pos_count + proc_neg_count

    if total_raw > 0:
        diff_pct = (total_proc - total_raw) / total_raw * 100
        print(f"\nTotal Diff:  {diff_pct:>+6.1f}% ({total_proc} vs {total_raw})")

    def print_table(title, raw_files, proc_files, raw_base, proc_base):
        print(f"\n{title}:")
        
        def group_by_source(files, base):
            groups = defaultdict(int)
            for f in files:
                name = get_source_name(f, base)
                groups[name] += 1
            return groups

        raw_groups = group_by_source(raw_files, raw_base)
        proc_groups = group_by_source(proc_files, proc_base)

        all_sources = sorted(set(list(raw_groups.keys()) + list(proc_groups.keys())))

        print(f"  {'Source Name':<30} | {'Raw':>6} | {'Proc':>6}")
        print(f"  {'-'*30}-+-{'-'*6}-+-{'-'*6}")
        for source in all_sources:
            r_c = raw_groups.get(source, 0)
            p_c = proc_groups.get(source, 0)
            s_name = source if len(source) <= 30 else source[:27] + "..."
            print(f"  {s_name:<30} | {r_c:>6} | {p_c:>6}")

    print_table("TARGET CLASS (1)", raw_pos_files, proc_pos_files, raw_pos_dir, proc_pos_dir)
    print_table("RANDOM CLASS (0)", raw_neg_files, proc_neg_files, raw_neg_dir, proc_neg_dir)


    # ---------------------------------------------------------
    # CSV Dataset Statistics
    # ---------------------------------------------------------
    csv_path = config.get("data", {}).get("dataset_csv", "data/processed/dataset.csv")
    print("\n" + "="*60)
    print("DATASET CSV STATISTICS")
    print("="*60)

    if not os.path.exists(csv_path):
        print(f"CSV file not found at: {csv_path}")
        print("Run 'python main.py build' to generate the dataset CSV.")
        return

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    total_frames = len(df)
    print(f"Total Configured Frames: {total_frames}\n")

    if total_frames == 0:
        print("Dataset is empty.")
        return

    # 1. Overall Class Balance
    print("--- Class Balance ---")
    class_counts = df['label'].value_counts().sort_index(ascending=False)
    for label, count in class_counts.items():
        class_name = "Target (1)" if label == 1 else "Random (0)"
        pct = (count / total_frames) * 100
        print(f"  {class_name:<12}: {count:>5} frames ({pct:>5.1f}%)")

    # 2. Split Distribution
    print("\n--- Split Distribution (Train/Val/Test) ---")
    if 'split' in df.columns:
        split_counts = df['split'].value_counts()
        for split_name, count in split_counts.items():
            pct = (count / total_frames) * 100
            print(f"  {split_name.capitalize():<12}: {count:>5} frames ({pct:>5.1f}%)")
        
        print("\n  [Breakdown by Class & Split]")
        cross_tab = pd.crosstab(df['label'], df['split'], margins=True, margins_name="Total")
        cross_tab.index = cross_tab.index.map(lambda x: "Target (1)" if x == 1 else ("Random (0)" if x == 0 else "Total"))
        
        # Format the cross_tab output to match indentation
        cross_tab_str = cross_tab.to_string()
        print("  " + cross_tab_str.replace("\n", "\n  "))
    else:
        print("  'split' column not found in CSV.")

    # 3. Video-Level Breakdown
    print("\n--- Video / Folder Breakdown ---")
    if 'video_name' in df.columns:
        
        # Create a display grouping to prevent thousands of scraped images from flooding the output
        df['display_name'] = df['video_name'].apply(
            lambda x: 'scraped (individual images)' if str(x).startswith('scraped_') else x
        )

        # Aggregate split name and frame count per video (grouping scraped images by split)
        video_stats = df.groupby(['label', 'display_name', 'split']).agg(
            frames=('filepath', 'count')
        ).reset_index()

        for label in [1, 0]:
            class_name = "TARGET (1)" if label == 1 else "RANDOM (0)"
            print(f"\n  {class_name} VIDEOS:")
            
            # Sort by split (test -> train -> val roughly) and then by frame size
            class_videos = video_stats[video_stats['label'] == label].sort_values(by=['split', 'frames'], ascending=[True, False])
            
            if class_videos.empty:
                print("    No videos found.")
                continue

            print(f"    {'Video Name':<40} | {'Split':<6} | {'Frames':>6}")
            print(f"    {'-'*40}-+-{'-'*6}-+-{'-'*6}")
            
            for _, row in class_videos.iterrows():
                v_name = str(row['display_name'])
                if len(v_name) > 40:
                    v_name = v_name[:37] + "..."
                print(f"    {v_name:<40} | {str(row['split']):<6} | {row['frames']:>6}")
    else:
        print("  'video_name' column not found in CSV.")

if __name__ == "__main__":
    import yaml
    import sys
    config_path = "config.yaml"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f)
        print_status(cfg)
    else:
        print("Run this script via 'python main.py status'")