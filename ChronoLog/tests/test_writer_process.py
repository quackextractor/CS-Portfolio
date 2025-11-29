import unittest
import tempfile
import json
import queue
import os
from src.writer_process import WriterProcess


class TestWriterProcess(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        # treat output_path as a directory
        self.out_dir = os.path.join(self.tmpdir.name, "out")
        os.makedirs(self.out_dir, exist_ok=True)

        # writer writes a timeline file named timeline.jsonl inside this dir
        self.timeline_path = os.path.join(self.out_dir, "timeline.jsonl")
        self.summary_path = os.path.join(self.out_dir, "summary.json")

        self.wp = WriterProcess(output_path=self.out_dir, flush_interval=0.01)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_update_aggregated_and_build_dashboard(self):
        delta = {"ERROR": ["e1"], "CUSTOM": ["c1", "c2"]}
        self.wp._update_aggregated(delta)
        self.assertIn("ERROR", self.wp.aggregated)
        self.assertIn("CUSTOM", self.wp.aggregated)
        summary = self.wp._build_dashboard()
        self.assertIsInstance(summary, dict)
        self.assertIn("summary", summary)
        self.assertEqual(summary["summary"]["error_count"], 1)

    def test_process_queue_writes_and_flush_creates_summary(self):
        q = queue.Queue()

        events = {"ERROR": ["Database failed"]}
        timeline = [
            {"time": "2025-11-23T12:00:00", "event": "error", "msg": "2025-11-23 12:00:00 ERROR Database failed"}
        ]
        q.put((events, timeline))

        # open writer’s actual timeline file path
        with open(self.timeline_path, "a", encoding="utf-8") as fh, \
             open(os.path.join(self.out_dir, "messages.jsonl"), "a", encoding="utf-8") as mfh:
            self.wp._process_queue(q, fh, mfh)

        with open(self.timeline_path, "r", encoding="utf-8") as fh:
            lines = [l.strip() for l in fh if l.strip()]
        self.assertTrue(len(lines) >= 1)

        self.wp.flush()
        self.assertTrue(os.path.exists(self.summary_path))

        with open(self.summary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("summary", data)
        self.assertGreaterEqual(data.get("timeline_count", 0), 1)

    def test_compute_metrics(self):
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