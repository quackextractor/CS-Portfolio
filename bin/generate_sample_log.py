"""
Generates a sample log file with errors, warnings, info, and latency events.
Place this in /bin and run to produce /examples/sample.log
"""

import random
from datetime import datetime, timedelta
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent.parent / "examples" / "sample.log"
NUM_LINES = 1_000_000  # number of log entries

ERRORS = [
    "Database connection failed",
    "Timeout on API call",
    "User authentication failed",
    "Disk write error"
]

WARNINGS = [
    "Slow query detected",
    "Memory usage high",
    "Cache miss rate high",
    "CPU usage > 80%"
]

INFO_MESSAGES = [
    "User login successful",
    "File uploaded",
    "Background job completed"
]

def random_latency():
    return random.randint(50, 500)  # ms

def generate_log_line(timestamp):
    r = random.random()
    if r < 0.2:
        msg = random.choice(ERRORS)
        level = "ERROR"
        return f"{timestamp} {level} {msg}"
    elif r < 0.5:
        msg = random.choice(WARNINGS)
        level = "WARNING"
        return f"{timestamp} {level} {msg}"
    elif r < 0.9:
        msg = random.choice(INFO_MESSAGES)
        level = "INFO"
        return f"{timestamp} {level} {msg}"
    else:
        latency = random_latency()
        level = "INFO"
        return f"{timestamp} {level} latency={latency}"

def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    start_time = datetime.now() - timedelta(minutes=30)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for i in range(NUM_LINES):
            ts = (start_time + timedelta(seconds=i*30)).strftime("%Y-%m-%d %H:%M:%S")
            line = generate_log_line(ts)
            f.write(line + "\n")
    print(f"Sample log generated at {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
