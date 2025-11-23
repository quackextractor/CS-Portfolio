import os
import sys
import unittest

# Ensure src is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=os.path.dirname(__file__), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=3)
    result = runner.run(suite)
    # Exit with non-zero if tests failed
    sys.exit(not result.wasSuccessful())