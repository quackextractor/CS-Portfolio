import json
import os
import re
import time
from config import OUTPUT_PATH, WRITER_FLUSH_INTERVAL

class WriterProcess:
    def __init__(self, output_path=OUTPUT_PATH, flush_interval=WRITER_FLUSH_INTERVAL):
        self.output_dir = output_path
        self.flush_interval = flush_interval
        self.aggregated = {}
        self.timeline = []
        self.msg_store = {}
        self.msg_id_counter = 0
        self.last_flush = time.time()

        os.makedirs(self.output_dir, exist_ok=True)

        self.timeline_path = os.path.join(self.output_dir, "timeline.jsonl")
        self.msg_file_path = os.path.join(self.output_dir, "messages.jsonl")
        self.summary_path = os.path.join(self.output_dir, "summary.json")

    def run(self, queue, stop_flag):
        with open(self.timeline_path, "a", encoding="utf-8") as timeline_file, \
             open(self.msg_file_path, "a", encoding="utf-8") as msg_file:

            try:
                while not stop_flag.is_set() or not queue.empty():
                    self._process_queue(queue, timeline_file, msg_file)
                    if self._should_flush():
                        self.flush()
            except KeyboardInterrupt:
                pass
            finally:
                while not queue.empty():
                    self._process_queue(queue, timeline_file, msg_file)
                self.flush()

    def _process_queue(self, queue, timeline_file, msg_file):
        try:
            delta_events, delta_timeline = queue.get(timeout=0.5)
            self._update_aggregated(delta_events)

            for entry in delta_timeline:
                msg_key = entry.get("msg")

                if msg_key:
                    stripped = re.sub(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} ", "", msg_key)

                    nums = re.findall(r"\b\d+\b", stripped)
                    tmpl = re.sub(r"\b\d+\b", "{num}", stripped)

                    msg_id = self.msg_store.get(tmpl)
                    if msg_id is None:
                        msg_id = self.msg_id_counter
                        self.msg_store[tmpl] = msg_id
                        self.msg_id_counter += 1

                        msg_file.write(json.dumps(
                            {"id": msg_id, "template": tmpl},
                            ensure_ascii=False
                        ) + "\n")

                    entry["msg_id"] = msg_id
                    if nums:
                        entry["msg_values"] = nums
                    del entry["msg"]

                self.timeline.append(entry)
                timeline_file.write(json.dumps(entry, ensure_ascii=False) + "\n")

        except Exception:
            pass

    def _update_aggregated(self, delta_events):
        if not delta_events:
            return
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
        tmp = self.summary_path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(dashboard, f)
            os.replace(tmp, self.summary_path)
        except Exception:
            pass

    def _build_dashboard(self):
        return {
            "summary": {
                "error_count": len(self.aggregated.get("ERROR", [])),
                "warning_count": len(self.aggregated.get("WARNING", [])),
                "metrics": self._compute_metrics()
            },
            "timeline_count": len(self.timeline),
            "unique_messages": len(self.msg_store)
        }

    def _compute_metrics(self):
        counts = {}
        sums = {}
        for t in self.timeline:
            if "value" not in t:
                continue
            name = t["event"]
            counts[name] = counts.get(name, 0) + 1
            sums[name] = sums.get(name, 0) + t["value"]

        return {
            name: {
                "count": cnt,
                "average": sums[name] / cnt if cnt else 0
            }
            for name, cnt in counts.items()
        }