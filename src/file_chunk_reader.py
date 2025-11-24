import time
from pathlib import Path
from config import CHUNK_SIZE, POLL_INTERVAL

class FileChunkReader:
    def __init__(self, file_path, chunk_size=CHUNK_SIZE, poll_interval=POLL_INTERVAL):
        self.file_path = Path(file_path).resolve()
        self.chunk_size = chunk_size
        self.poll_interval = poll_interval
        self.eof_reached = False

    def __iter__(self):
        with open(self.file_path, "r", encoding="utf-8", errors="replace") as f:
            while True:
                chunk = self._read_chunk(f)
                if chunk:
                    yield chunk
                else:
                    if not self.eof_reached:
                        self.eof_reached = True
                        print("EOF reached. Waiting for user to stop the program (Ctrl+C).")
                    time.sleep(self.poll_interval)

    def _read_chunk(self, file_obj):
        lines = [file_obj.readline() for _ in range(self.chunk_size)]
        return [l for l in lines if l]