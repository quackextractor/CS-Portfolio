import json
import queue
from pathlib import Path
from writer_process import WriterProcess


def test_process_queue_writes_and_deduplicates(tmp_path):
    out = tmp_path / "out.jsonl"
    writer = WriterProcess(output_path=str(out), flush_interval=0.001)

    q = queue.Queue()
    # first entry contains a message string that will be deduplicated into a template
    delta_events = {"ERROR": ["Database connection failed"]}
    delta_timeline = [
        {"time": "2025-11-23T12:00:00", "event": "error", "msg": "2025-11-23 12:00:00 ERROR Database connection failed"},
        {"time": "2025-11-23T12:01:00", "event": "latency", "value": 42},
    ]
    q.put((delta_events, delta_timeline))

    # open file handle for appending as WriterProcess.run would
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "a", encoding="utf-8") as fh:
        writer._process_queue(q, fh)

    # internal structures updated
    assert "ERROR" in writer.aggregated
    assert len(writer.timeline) == 2
    # msg_store should have at least one template entry (for the msg)
    assert len(writer.msg_store) >= 1

    # file should contain lines (template + timeline entries)
    with open(out, "r", encoding="utf-8") as fh:
        lines = [l.strip() for l in fh.readlines() if l.strip()]
    assert len(lines) >= 2


def test_flush_creates_summary_file(tmp_path):
    out = tmp_path / "out2.jsonl"
    writer = WriterProcess(output_path=str(out), flush_interval=0.001)

    # populate internal structures so summary is meaningful
    writer.aggregated = {"ERROR": ["e1", "e2"], "WARNING": ["w1"]}
    writer.timeline = [
        {"time": "t1", "event": "latency", "value": 100},
        {"time": "t2", "event": "latency", "value": 200},
    ]
    writer.msg_store = {"template1": 0}

    # call flush and verify summary file exists and content matches expected counts
    writer.flush()
    summary_path = str(out) + ".summary.json"
    assert Path(summary_path).exists()

    with open(summary_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    summary = data.get("summary", {})
    assert summary.get("error_count") == 2
    assert summary.get("warning_count") == 1
    # metrics should report latency average = 150
    metrics = summary.get("metrics", {})
    assert "latency" in metrics
    assert metrics["latency"]["count"] == 2
    assert metrics["latency"]["average"] == 150.0
