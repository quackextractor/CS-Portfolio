import argparse
import time
from config import INPUT_FILE_PATH
from log_processor import LogProcessor

def parse_args():
    p = argparse.ArgumentParser(description="ChronoLog processor")
    p.add_argument(
        "--mode",
        choices=("live", "batch"),
        default="batch",  # changed default
        help="live = keep tailing file until interrupted; batch = process current data and exit"
    )
    p.add_argument(
        "--input",
        help="override input file path",
        default=None
    )
    return p.parse_args()

if __name__ == "__main__":
    start_time = time.time()

    args = parse_args()
    input_path = args.input or INPUT_FILE_PATH
    live_mode = args.mode == "live"

    LogProcessor(input_path).start(live=live_mode)

    end_time = time.time()
    elapsed = end_time - start_time
    print(f"Processing finished in {elapsed:.2f} seconds.")