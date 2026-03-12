import os
import glob
from collections import defaultdict
from pathlib import Path


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
            # It's in a subfolder, use the subfolder name as the source
            return parts[0]
    except ValueError:
        pass
    
    # Fallback to filename-based naming if not in a subfolder or error
    filename = os.path.basename(file_path)
    if "_frame_" in filename:
        return filename.split("_frame_")[0]
    
    # Fallback: take everything before the last underscore if it looks like a frame number
    base = os.path.splitext(filename)[0]
    parts_list = base.split("_")
    if len(parts_list) > 1 and parts_list[-1].isdigit():
        return "_".join(parts_list[:-1])
        
    return "root"


def print_status(config):
    """Calculates and prints the dataset status."""
    raw_pos_dir = config["data"]["raw_positive_dir"]
    raw_neg_dir = config["data"]["raw_negative_dir"]
    proc_dir = config["data"]["processed_dir"]

    proc_pos_dir = os.path.join(proc_dir, "positive")
    proc_neg_dir = os.path.join(proc_dir, "negative")

    # Raw stats
    raw_pos_count, raw_pos_size, raw_pos_files = get_dir_stats(raw_pos_dir)
    raw_neg_count, raw_neg_size, raw_neg_files = get_dir_stats(raw_neg_dir)

    # Processed stats
    proc_pos_count, proc_pos_size, proc_pos_files = get_dir_stats(proc_pos_dir)
    proc_neg_count, proc_neg_size, proc_neg_files = get_dir_stats(proc_neg_dir)

    print("\n" + "="*40)
    print(" TARGET DATASET STATUS REPORT ")
    print("="*40)

    print("\nRAW DATA:")
    print(f"  Positive:  {raw_pos_count:>5} frames  ({raw_pos_size:>7.2f} MB)")
    print(f"  Negative:  {raw_neg_count:>5} frames  ({raw_neg_size:>7.2f} MB)")

    print("\nPROCESSED DATA:")
    print(f"  Positive:  {proc_pos_count:>5} frames  ({proc_pos_size:>7.2f} MB)")
    print(f"  Negative:  {proc_neg_count:>5} frames  ({proc_neg_size:>7.2f} MB)")

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
        print(f"  {'-'*30}-|{'-'*8}|{'-'*8}")
        for source in all_sources:
            r_cnt = raw_groups.get(source, 0)
            p_cnt = proc_groups.get(source, 0)
            print(f"  {source[:30]:<30} | {r_cnt:>6} | {p_cnt:>6}")

    # Grouping by Video / Source
    print_table("POSITIVE FRAMES BY SOURCE (SUBTOTALS)", raw_pos_files, proc_pos_files, raw_pos_dir, proc_pos_dir)
    print_table("NEGATIVE FRAMES BY SOURCE (SUBTOTALS)", raw_neg_files, proc_neg_files, raw_neg_dir, proc_neg_dir)

    print("="*40 + "\n")
