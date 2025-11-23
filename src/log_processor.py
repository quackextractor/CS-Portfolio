import multiprocessing
import time
from config import INPUT_FILE_PATH, NUM_PROCESSES, QUEUE_MAX_SIZE, QUEUE_PUT_TIMEOUT
from log_parser import LogParser
from file_chunk_reader import FileChunkReader
from writer_process import WriterProcess

class LogProcessor:
    def __init__(self, input_file=INPUT_FILE_PATH, num_processes=NUM_PROCESSES):
        self.input_file = input_file
        self.num_processes = num_processes
        self.parser = LogParser()
        self.queue = multiprocessing.Queue(maxsize=QUEUE_MAX_SIZE)
        self.stop_flag = multiprocessing.Event()

    def start(self):
        writer_proc = multiprocessing.Process(
            target=WriterProcess().run,
            args=(self.queue, self.stop_flag)
        )
        writer_proc.start()

        pool = multiprocessing.Pool(self.num_processes)
        reader = FileChunkReader(self.input_file)
        try:
            for chunk in reader:
                pool.apply_async(
                    self.parser.parse_lines,
                    args=(chunk,),
                    callback=self._on_result,
                    error_callback=self._on_error
                )
        except KeyboardInterrupt:
            print("User requested stop.")
            self._handle_interrupt(pool)
        finally:
            self._shutdown(pool, writer_proc)

    def _on_result(self, result):
        events, timeline = result
        self._safe_queue_put((events, timeline))

    def _safe_queue_put(self, item):
        retries = 3
        for _ in range(retries):
            try:
                self.queue.put(item, timeout=QUEUE_PUT_TIMEOUT)
                return
            except Exception:
                time.sleep(0.1)
        print("Warning: dropped log chunk due to full queue")

    def _on_error(self, exc):
        print("worker error:", exc)

    def _handle_interrupt(self, pool):
        self.stop_flag.set()
        pool.terminate()
        pool.join()

    def _shutdown(self, pool, writer_proc):
        pool.close()
        pool.join()
        self.stop_flag.set()
        writer_proc.join(timeout=10)
        if writer_proc.is_alive():
            writer_proc.terminate()
            writer_proc.join()