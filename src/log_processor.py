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

    def start(self, live=True):
        """
        live=True  -> keep tailing the file until interrupted
        live=False -> read available data, process, then exit once processing is complete
        """
        writer_proc = multiprocessing.Process(
            target=WriterProcess().run,
            args=(self.queue, self.stop_flag)
        )
        writer_proc.start()

        pool = multiprocessing.Pool(self.num_processes)
        reader = FileChunkReader(self.input_file, live=live)
        try:
            for chunk in reader:
                pool.apply_async(
                    self.parser.parse_lines,
                    args=(chunk,),
                    callback=self._on_result,
                    error_callback=self._on_error
                )

            # If reader finished normally (batch mode), close the pool and wait for workers to finish.
            if not live:
                pool.close()
                pool.join()
                # All worker callbacks have been invoked or will be. Signal writer to finish after it drains the queue.
                self.stop_flag.set()

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
        try:
            pool.terminate()
        except Exception:
            pass
        pool.join()

    def _shutdown(self, pool, writer_proc):
        # If pool wasn't closed (live mode or interrupted), attempt graceful close then join.
        try:
            pool.close()
        except Exception:
            pass
        try:
            pool.join()
        except Exception:
            pass

        # Ensure writer is signalled to stop (if not already).
        self.stop_flag.set()

        # Wait for writer to finish writing remaining queued items.
        writer_proc.join(timeout=10)
        if writer_proc.is_alive():
            try:
                writer_proc.terminate()
            except Exception:
                pass
            writer_proc.join()