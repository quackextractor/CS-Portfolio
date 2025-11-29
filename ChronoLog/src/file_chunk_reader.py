import time
from pathlib import Path
from config import CHUNK_SIZE, POLL_INTERVAL

class FileChunkReader:
    def __init__(self, file_path, chunk_size=CHUNK_SIZE, poll_interval=POLL_INTERVAL, live=True):
        self.file_path = Path(file_path).resolve()
        self.chunk_size = chunk_size
        self.poll_interval = poll_interval
        self.eof_reached = False
        self.live = live

    def __iter__(self):
        with open(self.file_path, "r", encoding="utf-8", errors="replace") as f:
            while True:
                chunk = self._read_chunk(f)
                if chunk:
                    # new data available
                    yield chunk
                    self.eof_reached = False
                else:
                    # no new data
                    if not self.eof_reached:
                        self.eof_reached = True
                        if self.live:
                            print("Reading completed.")
                        else:
                            # batch mode: stop iteration and let caller finish processing
                            return
                    if self.live:
                        time.sleep(self.poll_interval)
                    else:
                        # batch mode: no need to loop/wait
                        return

    def _read_chunk(self, file_obj):
        lines = [file_obj.readline() for _ in range(self.chunk_size)]
        return [l for l in lines if l]