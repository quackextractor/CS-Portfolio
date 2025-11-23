import json
import os
import re
import time
from config import OUTPUT_PATH, WRITER_FLUSH_INTERVAL

class WriterProcess:
    def __init__(self, output_path=OUTPUT_PATH, flush_interval=WRITER_FLUSH_INTERVAL):
        self.output_path = output_path
        self.flush_interval = flush_interval
        self.aggregated = {}
        self.timeline = []
        self.msg_store = {}          # maps message string -> ID
        self.msg_id_counter = 0
        self.last_flush = time.time()

    def run(self, queue, stop_flag):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, "a", encoding="utf-8") as jsonl_file:
            try:
                while not stop_flag.is_set() or not queue.empty():
                    self._process_queue(queue, jsonl_file)
                    if self._should_flush():
                        self.flush()
            except KeyboardInterrupt:
                print("Writer received stop signal. Flushing remaining data...")
            finally:
                while not queue.empty():
                    self._process_queue(queue, jsonl_file)
                self.flush()

    def _process_queue(self, queue, jsonl_file):
        try:
            delta_events, delta_timeline = queue.get(timeout=0.5)
            self._update_aggregated(delta_events)

            for entry in delta_timeline:
                msg_key = entry.get("msg")
                if msg_key:
                    # deduplicate by stripping timestamp & numeric values for template
                    msg_template = re.sub(r"\b\d+\b", "{num}", msg_key)
                    msg_template = re.sub(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} ", "", msg_template)

                    msg_id = self.msg_store.get(msg_template)
                    if msg_id is None:
                        msg_id = self.msg_id_counter
                        self.msg_store[msg_template] = msg_id
                        self.msg_id_counter += 1
                        # write unique message template
                        jsonl_file.write(
                            json.dumps({"id": msg_id, "template": msg_template}, ensure_ascii=False) + "\n")

                    entry["msg_id"] = msg_id
                    del entry["msg"]

                self.timeline.append(entry)
                jsonl_file.write(json.dumps(entry, ensure_ascii=False) + "\n")

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
        dashboard_path = self.output_path + ".summary.json"
        try:
            with open(dashboard_path + ".tmp", "w", encoding="utf-8") as f:
                json.dump(dashboard, f)
            os.replace(dashboard_path + ".tmp", dashboard_path)
        except Exception:
            pass

    def _build_dashboard(self):
        summary = {
            "error_count": len(self.aggregated.get("ERROR", [])),
            "warning_count": len(self.aggregated.get("WARNING", []))
        }
        metrics = self._compute_metrics()
        summary["metrics"] = metrics
        return {"summary": summary, "timeline_count": len(self.timeline), "unique_messages": len(self.msg_store)}

    def _compute_metrics(self):
        counts = {}
        sums = {}
        for t in self.timeline:
            if "value" in t:
                name = t["event"]
                counts[name] = counts.get(name, 0) + 1
                sums[name] = sums.get(name, 0) + t["value"]
        return {name: {"count": cnt, "average": sums[name] / cnt if cnt else 0} for name, cnt in counts.items()}