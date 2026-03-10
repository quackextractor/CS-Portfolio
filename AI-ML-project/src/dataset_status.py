import os
import glob
from pathlib import Path
from collections import defaultdict

def get_dir_stats(directory):
    """Calculates count and total size in MB of files in a directory."""
    files = glob.glob(os.path.join(directory, "*.*"))
    count = len(files)
    total_size = sum(os.path.getsize(f) for f in files) / (1024 * 1024)
    return count, total_size, files

def get_video_name(filename):
    """
    Extracts video name from filename.
    Assumes format like 'video_name_frame_0000.jpg' or similar.
    We look for the pattern before '_frame_'.
    """
    if "_frame_" in filename:
        return filename.split("_frame_")[0]
    # Fallback: take everything before the last underscore if it looks like a frame number
    base = os.path.splitext(filename)[0]
    parts = base.split("_")
    if len(parts) > 1 and parts[-1].isdigit():
        return "_".join(parts[:-1])
    return "unknown"

def print_status(config):
    """Calculates and prints the dataset status."""
    raw_pos_dir = config["data"]["raw_positive_dir"]
    raw_neg_dir = config["data"]["raw_negative_dir"]
    proc_dir = config["data"]["processed_dir"]
    
    proc_pos_dir = os.path.join(proc_dir, "positive")
    proc_neg_dir = os.path.join(proc_dir, "negative")

    # Raw stats
    raw_pos_count, raw_pos_size, raw_pos_files = get_dir_stats(raw_pos_dir)
    raw_neg_count, raw_neg_size, _ = get_dir_stats(raw_neg_dir)

    # Processed stats
    proc_pos_count, proc_pos_size, proc_pos_files = get_dir_stats(proc_pos_dir)
    proc_neg_count, proc_neg_size, _ = get_dir_stats(proc_neg_dir)

    print("\n" + "="*40)
    print(" MIRO DATASET STATUS REPORT ")
    print("="*40)

    print(f"\nRAW DATA:")
    print(f"  Positive:  {raw_pos_count:>5} frames  ({raw_pos_size:>7.2f} MB)")
    print(f"  Negative:  {raw_neg_count:>5} frames  ({raw_neg_size:>7.2f} MB)")

    print(f"\nPROCESSED DATA:")
    print(f"  Positive:  {proc_pos_count:>5} frames  ({proc_pos_size:>7.2f} MB)")
    print(f"  Negative:  {proc_neg_count:>5} frames  ({proc_neg_size:>7.2f} MB)")

    # Calculations
    total_raw = raw_pos_count + raw_neg_count
    total_proc = proc_pos_count + proc_neg_count
    
    if total_raw > 0:
        diff_pct = (total_proc - total_raw) / total_raw * 100
        print(f"\nTotal Diff:  {diff_pct:>+6.1f}% ({total_proc} vs {total_raw})")

    # Grouping by Video
    print("\nPOSITIVE FRAMES BY VIDEO (SUBTOTALS):")
    
    def group_by_video(files):
        groups = defaultdict(int)
        for f in files:
            name = get_video_name(os.path.basename(f))
            groups[name] += 1
        return groups

    raw_video_groups = group_by_video(raw_pos_files)
    proc_video_groups = group_by_video(proc_pos_files)

    all_videos = sorted(set(list(raw_video_groups.keys()) + list(proc_video_groups.keys())))

    print(f"  {'Video Source':<30} | {'Raw':>6} | {'Proc':>6}")
    print(f"  {'-'*30}-|{'-'*8}|{'-'*8}")
    for video in all_videos:
        r_cnt = raw_video_groups.get(video, 0)
        p_cnt = proc_video_groups.get(video, 0)
        print(f"  {video[:30]:<30} | {r_cnt:>6} | {p_cnt:>6}")

    print("="*40 + "\n")
