import os
import re

# Config
INPUT_FILE_PATH = os.getenv("INPUT_FILE_PATH", "../input/sample.log")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "../output/output.json")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "5000"))
QUEUE_MAX_SIZE = int(os.getenv("QUEUE_MAX_SIZE", "100"))
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "0.5"))
NUM_PROCESSES = int(os.getenv("NUM_PROCESSES", "3"))
WRITER_FLUSH_INTERVAL = 2.0
QUEUE_PUT_TIMEOUT = 1.0  # avoid blocking forever

TRACK_VARIABLES = [v.strip() for v in os.getenv("TRACK_VARIABLES", "").split(",") if v.strip()]
VAR_REGEX = {var: re.compile(rf"\b{re.escape(var)}=(\d+)\b") for var in TRACK_VARIABLES} if TRACK_VARIABLES else None
KEY_VAL_RE = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)=(\d+)\b")