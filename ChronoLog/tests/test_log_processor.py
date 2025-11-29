import unittest
import queue
from src.log_processor import LogProcessor


class DummyPool:
    def __init__(self):
        self.terminated = False
        self.joined = False

    def terminate(self):
        self.terminated = True

    def join(self):
        self.joined = True


class TestLogProcessor(unittest.TestCase):
    def setUp(self):
        # create processor then replace its queue with a local queue.Queue for tests
        self.lp = LogProcessor(num_processes=1)
        self.lp.queue = queue.Queue()

    def test_safe_queue_put_and_on_result(self):
        # use _safe_queue_put directly
        item = ("ev", "tl")
        self.lp._safe_queue_put(item)
        got = self.lp.queue.get_nowait()
        self.assertEqual(got, item)
        # test _on_result uses safe_queue_put
        self.lp._on_result(({"ERROR": []}, [{"time": None, "event": "error", "msg": "m"}]))
        ev, tl = self.lp.queue.get_nowait()
        self.assertIsInstance(ev, dict)
        self.assertIsInstance(tl, list)

    def test_handle_interrupt_sets_stop_and_terminates_pool(self):
        pool = DummyPool()
        # ensure stop_flag initially not set
        self.assertFalse(self.lp.stop_flag.is_set())
        self.lp._handle_interrupt(pool)
        self.assertTrue(self.lp.stop_flag.is_set())
        self.assertTrue(pool.terminated)
        self.assertTrue(pool.joined)


if __name__ == "__main__":
    unittest.main()
