import unittest
import tempfile
import json
import queue
import os
from src.writer_process import WriterProcess


class TestWriterProcess(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.out_path = os.path.join(self.tmpdir.name, "out.jsonl")
        self.wp = WriterProcess(output_path=self.out_path, flush_interval=0.01)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_update_aggregated_and_build_dashboard(self):
        delta = {"ERROR": ["e1"], "CUSTOM": ["c1", "c2"]}
        self.wp._update_aggregated(delta)
        # aggregated should now include keys
        self.assertIn("ERROR", self.wp.aggregated)
        self.assertIn("CUSTOM", self.wp.aggregated)
        summary = self.wp._build_dashboard()
        self.assertIsInstance(summary, dict)
        self.assertIn("summary", summary)
        self.assertEqual(summary["summary"]["error_count"], 1)

    def test_process_queue_writes_and_flush_creates_summary(self):
        q = queue.Queue()
        # events + timeline with a msg that will be deduped into a template
        events = {"ERROR": ["Database failed"]}
        timeline = [
            {"time": "2025-11-23T12:00:00", "event": "error", "msg": "2025-11-23 12:00:00 ERROR Database failed"}
        ]
        q.put((events, timeline))
        # open the same file path in append mode and call _process_queue
        with open(self.out_path, "a", encoding="utf-8") as fh:
            self.wp._process_queue(q, fh)
        # file should now contain at least one JSON line for the template and one for the entry
        with open(self.out_path, "r", encoding="utf-8") as fh:
            lines = [l.strip() for l in fh if l.strip()]
        self.assertTrue(len(lines) >= 2)
        # flush to create summary file
        self.wp.flush()
        summary_path = self.out_path + ".summary.json"
        self.assertTrue(os.path.exists(summary_path))
        with open(summary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("summary", data)
        # timeline_count should be >=1
        self.assertGreaterEqual(data.get("timeline_count", 0), 1)

    def test_compute_metrics(self):
        # craft timeline with value-bearing entries
        self.wp.timeline = [
            {"event": "latency", "value": 100},
            {"event": "latency", "value": 200},
            {"event": "other", "value": 10}
        ]
        metrics = self.wp._compute_metrics()
        self.assertIn("latency", metrics)
        self.assertEqual(metrics["latency"]["count"], 2)
        self.assertEqual(metrics["latency"]["average"], 150.0)
        self.assertEqual(metrics["other"]["count"], 1)


if __name__ == "__main__":
    unittest.main()