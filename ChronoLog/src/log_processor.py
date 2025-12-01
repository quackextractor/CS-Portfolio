import multiprocessing
import time
from config import INPUT_FILE_PATH, NUM_PROCESSES, QUEUE_MAX_SIZE, QUEUE_PUT_TIMEOUT, NUM_WRITERS
from log_parser import LogParser
from file_chunk_reader import FileChunkReader
from writer_process import WriterProcess

class LogProcessor:
    def __init__(self, input_file=INPUT_FILE_PATH, num_processes=NUM_PROCESSES, num_writers=NUM_WRITERS):
        self.input_file = input_file
        self.num_processes = num_processes
        self.num_writers = num_writers
        self.parser = LogParser()
        self.queue = multiprocessing.Queue(maxsize=QUEUE_MAX_SIZE)
        self.stop_flag = multiprocessing.Event()

    def start(self, live=True):
        """
        live=True  -> keep tailing the file until interrupted
        live=False -> read available data, process, then exit once processing is complete
        """
        writers = []
        for _ in range(self.num_writers):
            wp = multiprocessing.Process(
                target=WriterProcess().run,
                args=(self.queue, self.stop_flag)
            )
            wp.start()
            writers.append(wp)

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
                # All worker callbacks have been invoked or will be. Signal writers to finish after they drain the queue.
                self.stop_flag.set()

        except KeyboardInterrupt:
            print("User requested stop.")
            self._handle_interrupt(pool)
        finally:
            self._shutdown(pool, writers)

    def _on_result(self, result):
        events, timeline = result
        self._safe_queue_put((events, timeline))

    def _safe_queue_put(self, item):
        # Implement backpressure: wait until queue has space
        while not self.stop_flag.is_set():
            try:
                self.queue.put(item, timeout=1.0)
                return
            except Exception: # queue.Full
                # Queue is full, wait and retry
                # In a real app, we might want to log this occasionally if it persists
                continue
        
        # If we get here, stop_flag is set, try one last time or just drop
        try:
            self.queue.put(item, timeout=0.1)
        except Exception:
            print("Warning: dropped log chunk during shutdown")

    def _on_error(self, exc):
        print("worker error:", exc)

    def _handle_interrupt(self, pool):
        self.stop_flag.set()
        try:
            pool.terminate()
        except Exception:
            pass
        pool.join()

    def _shutdown(self, pool, writers):
        # If pool wasn't closed (live mode or interrupted), attempt graceful close then join.
        try:
            pool.close()
        except Exception:
            pass
        try:
            pool.join()
        except Exception:
            pass

        # Ensure writers are signalled to stop (if not already).
        self.stop_flag.set()

        # Wait for writers to finish writing remaining queued items.
        for wp in writers:
            wp.join(timeout=10)
            if wp.is_alive():
                try:
                    wp.terminate()
                except Exception:
                    pass
                wp.join()