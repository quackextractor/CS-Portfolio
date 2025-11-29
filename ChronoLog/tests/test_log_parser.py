import unittest
from datetime import datetime
from src.log_parser import LogParser


class TestLogParser(unittest.TestCase):
    def setUp(self):
        # use default behavior (KEY_VAL_RE and VAR_REGEX from config)
        self.parser = LogParser(var_regex=None)

    def test_extract_timestamp_valid(self):
        line = "2025-11-23 12:34:56 INFO something happened"
        ts = self.parser.extract_timestamp(line)
        # should be ISO format and match the original date/time
        self.assertIsNotNone(ts)
        self.assertTrue(ts.startswith("2025-11-23T12:34:56"))

    def test_parse_lines_errors_and_warnings(self):
        lines = [
            "2025-11-23 12:00:00 ERROR Database connection failed",
            "2025-11-23 12:01:00 WARNING Memory usage high",
            ""  # blank should be ignored
        ]
        events, timeline = self.parser.parse_lines(lines)
        self.assertIn("ERROR", events)
        self.assertIn("WARNING", events)
        self.assertEqual(len(events["ERROR"]), 1)
        self.assertEqual(len(events["WARNING"]), 1)
        # timeline should have entries for both events
        event_names = {e["event"] for e in timeline}
        self.assertIn("error", event_names)
        self.assertIn("warning", event_names)

    def test_parse_variables_with_keyval(self):
        lines = ["2025-11-23 12:10:00 INFO processed=7 size=123"]
        events, timeline = self.parser.parse_lines(lines)
        # KEY_VAL_RE should capture processed and size
        self.assertIn("processed", events)
        self.assertIn("size", events)
        # timeline should include entries with "value" keys for those metrics
        values = [t.get("value") for t in timeline if "value" in t]
        self.assertIn(7, values)
        self.assertIn(123, values)

    def test_parse_variables_with_var_regex(self):
        # supply a custom var_regex to only capture latency
        p = LogParser(var_regex={"latency": __import__("re").compile(r"latency=(\d+)")})
        lines = ["2025-11-23 12:11:00 INFO latency=250", "2025-11-23 12:12:00 INFO latency=120"]
        events, timeline = p.parse_lines(lines)
        self.assertIn("latency", events)
        self.assertEqual(len(events["latency"]), 2)
        vals = [t["value"] for t in timeline if t.get("event") == "latency"]
        self.assertCountEqual(vals, [250, 120])


if __name__ == "__main__":
    unittest.main()
