import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from config import INPUT_FILE_PATH
from file_chunk_reader import FileChunkReader
from log_parser import LogParser

def debug_pipeline():
    print(f"Testing pipeline with input: {INPUT_FILE_PATH}")
    
    if not os.path.exists(INPUT_FILE_PATH):
        print("ERROR: Input file does not exist!")
        return

    print(f"File size: {os.path.getsize(INPUT_FILE_PATH)} bytes")

    reader = FileChunkReader(INPUT_FILE_PATH, live=False)
    parser = LogParser()
    
    chunk_count = 0
    total_lines = 0
    total_events = 0
    
    start_time = time.time()
    
    for chunk in reader:
        chunk_count += 1
        total_lines += len(chunk)
        events, timeline = parser.parse_lines(chunk)
        total_events += len(timeline)
        
        if chunk_count % 10 == 0:
            print(f"Processed {chunk_count} chunks, {total_lines} lines...")

    end_time = time.time()
    
    print(f"Done in {end_time - start_time:.2f}s")
    print(f"Total chunks: {chunk_count}")
    print(f"Total lines: {total_lines}")
    print(f"Total events: {total_events}")

if __name__ == "__main__":
    debug_pipeline()
