import unittest
import tempfile
from src.file_chunk_reader import FileChunkReader

class TestFileChunkReader(unittest.TestCase):
    def setUp(self):
        # create a temp file with known content
        self.tmp = tempfile.NamedTemporaryFile(mode="w+", delete=False, encoding="utf-8")
        self.lines = [f"line {i}\n" for i in range(1, 6)]  # 5 lines
        self.tmp.writelines(self.lines)
        self.tmp.flush()
        self.tmp.close()
        self.reader = FileChunkReader(self.tmp.name, chunk_size=2, poll_interval=0.01)

    def tearDown(self):
        try:
            import os
            os.unlink(self.tmp.name)
        except Exception:
            pass

    def test_read_chunk_splits_lines(self):
        with open(self.tmp.name, "r", encoding="utf-8") as f:
            chunk1 = self.reader._read_chunk(f)
            chunk2 = self.reader._read_chunk(f)
            chunk3 = self.reader._read_chunk(f)
        # sizes: 2,2,1
        self.assertEqual(len(chunk1), 2)
        self.assertEqual(len(chunk2), 2)
        self.assertEqual(len(chunk3), 1)
        # content checks
        self.assertEqual(chunk1[0].strip(), "line 1")
        self.assertEqual(chunk3[0].strip(), "line 5")


if __name__ == "__main__":
    unittest.main()