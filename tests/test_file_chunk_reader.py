from pathlib import Path
import tempfile

from file_chunk_reader import FileChunkReader


def test__read_chunk_returns_expected_counts(tmp_path):
    p = tmp_path / "log.txt"
    lines = [f"line {i}\n" for i in range(10)]
    p.write_text("".join(lines), encoding="utf-8")

    reader = FileChunkReader(str(p), chunk_size=3, poll_interval=0.01)

    with open(p, "r", encoding="utf-8", errors="replace") as f:
        # read 3
        c1 = reader._read_chunk(f)
        assert len(c1) == 3
        # read 3
        c2 = reader._read_chunk(f)
        assert len(c2) == 3
        # read 3
        c3 = reader._read_chunk(f)
        assert len(c3) == 3
        # read remaining 1
        c4 = reader._read_chunk(f)
        assert len(c4) == 1
        # no more
        c5 = reader._read_chunk(f)
        assert c5 == []