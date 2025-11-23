import re
from log_parser import LogParser
from datetime import datetime


def test_extract_timestamp_valid_and_invalid():
    p = LogParser()
    ts = p.extract_timestamp("2025-11-23 12:00:00 INFO something")
    assert ts is not None
    # invalid timestamp
    ts2 = p.extract_timestamp("no-timestamp WARNING hi")
    assert ts2 is None


def test_parse_lines_errors_warnings_and_keyvals():
    lines = [
        "2025-11-23 12:00:00 INFO User login successful",
        "2025-11-23 12:01:00 ERROR Database connection failed",
        "bad line no-ts WARNING Something happened",
        "2025-11-23 12:02:00 INFO latency=123",
        "2025-11-23 12:03:00 INFO value=10 key=5"
    ]
    p = LogParser()  # uses KEY_VAL_RE for variables
    events, timeline = p.parse_lines(lines)

    # ERROR should be present
    assert "ERROR" in events
    assert any("Database connection failed" in e for e in events["ERROR"])
    # WARNING added from the bad line
    assert "WARNING" in events
    assert any("Something happened" in e for e in events["WARNING"])

    # timeline should include entries for variable parses (latency/value/key)
    names = [t.get("event") for t in timeline]
    assert "latency" in names or "value" in names or "key" in names

    # check that value entries have 'value' key
    assert any("value" in t for t in timeline)


def test_parse_with_var_regex_overrides_keyval():
    rx = {"latency": re.compile(r"latency=(\d+)")}
    p = LogParser(var_regex=rx)
    lines = ["2025-11-23 12:00:00 INFO latency=250", "2025-11-23 12:01:00 INFO latency=100"]
    events, timeline = p.parse_lines(lines)

    # var_regex should create 'latency' key with two entries
    assert "latency" in events
    assert len(events["latency"]) == 2

    # timeline should contain two entries with value and event 'latency'
    lat_entries = [t for t in timeline if t.get("event") == "latency"]
    assert len(lat_entries) == 2
    assert all("value" in t for t in lat_entries)