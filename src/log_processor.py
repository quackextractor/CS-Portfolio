import multiprocessing
import os
import time
import json
import re
from datetime import datetime

# Config
INPUT_FILE_PATH = os.getenv("INPUT_FILE_PATH", "../examples/sample.log")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "5000"))
QUEUE_MAX_SIZE = int(os.getenv("QUEUE_MAX_SIZE", "100"))
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "../output/output.json")
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "0.5"))
NUM_PROCESSES = int(os.getenv("NUM_PROCESSES", "3"))
WRITER_FLUSH_INTERVAL = 2.0
QUEUE_PUT_TIMEOUT = 1.0  # avoid blocking forever

TRACK_VARIABLES = [v.strip() for v in os.getenv("TRACK_VARIABLES", "").split(",") if v.strip()]
VAR_REGEX = {var: re.compile(rf"\b{re.escape(var)}=(\d+)\b") for var in TRACK_VARIABLES} if TRACK_VARIABLES else None
KEY_VAL_RE = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)=(\d+)\b")


class LogParser:
    def __init__(self, var_regex=None):
        self.var_regex = var_regex
        self.key_val_re = KEY_VAL_RE

    def parse_lines(self, lines):
        events = {"ERROR": [], "WARNING": []}
        timeline = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            timestamp = self.extract_timestamp(line)
            self.parse_errors_warnings(line, timestamp, events, timeline)
            self.parse_variables(line, timestamp, events, timeline)

        return events, timeline

    def extract_timestamp(self, line):
        time_str = line.split(" ", 2)[:2]
        ts = " ".join(time_str)
        try:
            return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").isoformat()
        except Exception:
            return None

    def parse_errors_warnings(self, line, timestamp, events, timeline):
        if "ERROR" in line:
            self._add_event("ERROR", line, "error", timestamp, events, timeline)
        if "WARNING" in line:
            self._add_event("WARNING", line, "warning", timestamp, events, timeline)

    def parse_variables(self, line, timestamp, events, timeline):
        if self.var_regex:
            for var, rx in self.var_regex.items():
                m = rx.search(line)
                if m:
                    val = int(m.group(1))
                    self._add_event(var, line, var, timestamp, events, timeline, val)
        else:
            for m in self.key_val_re.finditer(line):
                key = m.group(1)
                val = int(m.group(2))
                if key.upper() in ("ERROR", "WARNING"):
                    continue
                self._add_event(key, line, key, timestamp, events, timeline, val)

    def _add_event(self, key, line, event_name, timestamp, events, timeline, value=None):
        events.setdefault(key, []).append(line)
        entry = {"time": timestamp, "event": event_name}
        if value is not None:
            entry["value"] = value
        else:
            entry["msg"] = line
        timeline.append(entry)


class FileChunkReader:
    def __init__(self, file_path, chunk_size=CHUNK_SIZE, poll_interval=POLL_INTERVAL):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.poll_interval = poll_interval

    def __iter__(self):
        with open(self.file_path, "r", encoding="utf-8", errors="replace") as f:
            while True:
                chunk = self._read_chunk(f)
                if chunk:
                    yield chunk
                else:
                    time.sleep(self.poll_interval)

    def _read_chunk(self, file_obj):
        lines = [file_obj.readline() for _ in range(self.chunk_size)]
        return [l for l in lines if l]


class WriterProcess:
    def __init__(self, output_path, flush_interval=WRITER_FLUSH_INTERVAL):
        self.output_path = output_path
        self.flush_interval = flush_interval
        self.aggregated = {}
        self.timeline = []
        self.last_flush = time.time()

    def run(self, queue, stop_flag):
        while not stop_flag.is_set() or not queue.empty():
            self._process_queue(queue)
            if self._should_flush():
                self.flush()
        self.flush()

    def _process_queue(self, queue):
        try:
            delta_events, delta_timeline = queue.get(timeout=0.5)
            self._update_aggregated(delta_events)
            self.timeline.extend(delta_timeline)
        except Exception:
            pass

    def _update_aggregated(self, delta_events):
        if delta_events:
            for k, v in delta_events.items():
                self.aggregated.setdefault(k, []).extend(v)

    def _should_flush(self):
        now = time.time()
        if now - self.last_flush >= self.flush_interval:
            self.last_flush = now
            return True
        return False

    def flush(self):
        dashboard = self._build_dashboard()
        self._write_dashboard(dashboard)

    def _build_dashboard(self):
        summary = {
            "error_count": len(self.aggregated.get("ERROR", [])),
            "warning_count": len(self.aggregated.get("WARNING", []))
        }
        metrics = self._compute_metrics()
        summary["metrics"] = metrics
        return {"summary": summary, "timeline": self.timeline}

    def _compute_metrics(self):
        counts = {}
        sums = {}
        for t in self.timeline:
            if "value" in t:
                name = t["event"]
                counts[name] = counts.get(name, 0) + 1
                sums[name] = sums.get(name, 0) + t["value"]
        return {name: {"count": cnt, "average": sums[name] / cnt if cnt else 0} for name, cnt in counts.items()}

    def _write_dashboard(self, dashboard):
        try:
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            tmp = self.output_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(dashboard, f)
            os.replace(tmp, self.output_path)
        except Exception:
            pass


class LogProcessor:
    def __init__(self, input_file, num_processes=NUM_PROCESSES):
        self.input_file = input_file
        self.num_processes = num_processes
        self.parser = LogParser(VAR_REGEX)
        self.queue = multiprocessing.Queue(maxsize=QUEUE_MAX_SIZE)
        self.stop_flag = multiprocessing.Event()

    def start(self):
        writer_proc = multiprocessing.Process(
            target=WriterProcess(OUTPUT_PATH).run,
            args=(self.queue, self.stop_flag)
        )
        writer_proc.start()

        pool = multiprocessing.Pool(self.num_processes)
        try:
            for chunk in FileChunkReader(self.input_file):
                pool.apply_async(
                    self.parser.parse_lines,
                    args=(chunk,),
                    callback=self._on_result,
                    error_callback=self._on_error
                )
        except KeyboardInterrupt:
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


if __name__ == "__main__":
    LogProcessor(INPUT_FILE_PATH).start()