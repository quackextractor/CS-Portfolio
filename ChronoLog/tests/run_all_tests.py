import sys
import unittest
from pathlib import Path

# Resolve project root (one level above tests/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Ensure project root is first in path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure src is also on path
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

if __name__ == "__main__":
    tests_dir = Path(__file__).parent
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(tests_dir), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=3)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())