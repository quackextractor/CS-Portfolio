import os
from pathlib import Path
import re

# Root dir = ChronoLog/ (directory containing config.py)
ROOT = Path(__file__).resolve().parent.parent

INPUT_DIR = ROOT / "input"
OUTPUT_DIR = ROOT / "output"

DEFAULT_INPUT_FILE = INPUT_DIR / "sample.log"

INPUT_FILE_PATH = Path(os.getenv("INPUT_FILE_PATH", DEFAULT_INPUT_FILE))
OUTPUT_PATH = Path(os.getenv("OUTPUT_PATH", OUTPUT_DIR))

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "5000"))
QUEUE_MAX_SIZE = int(os.getenv("QUEUE_MAX_SIZE", "100"))
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "0.5"))
NUM_PROCESSES = int(os.getenv("NUM_PROCESSES", "3"))
WRITER_FLUSH_INTERVAL = 2.0
QUEUE_PUT_TIMEOUT = 1.0

TRACK_VARIABLES = [v.strip() for v in os.getenv("TRACK_VARIABLES", "").split(",") if v.strip()]
VAR_REGEX = {var: re.compile(rf"\b{re.escape(var)}=(\d+)\b") for var in TRACK_VARIABLES} if TRACK_VARIABLES else None
KEY_VAL_RE = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)=(\d+)\b")