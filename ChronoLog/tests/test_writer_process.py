import unittest
class TestWriterProcess(unittest.TestCase):
    def setUp(self):
        # Patch the facade class where it is imported in writer_process
        self.facade_patcher = patch('src.writer_process.ChronoLogFacade')
        self.MockFacade = self.facade_patcher.start()
        self.mock_facade_instance = self.MockFacade.return_value
        
        # Initialize WriterProcess
        self.wp = WriterProcess(flush_interval=0.01)

    def tearDown(self):
        self.facade_patcher.stop()

    def test_init(self):
        """Test initialization of WriterProcess."""
        self.assertEqual(self.wp.flush_interval, 0.01)
        self.assertEqual(self.wp.facade, self.mock_facade_instance)
        self.assertEqual(self.wp.msg_cache, {})

    def test_prepare_entry_valid(self):
        """Test _prepare_entry with valid data."""
        entry = {
            "time": "2023-10-27T10:00:00",
            "event": "INFO",
            "msg": "2023-10-27 10:00:00 INFO User 123 logged in",
            "value": None
        }
        
        # Mock facade behavior
        self.mock_facade_instance.get_or_create_message_id.return_value = 5
        
        result = self.wp._prepare_entry(entry)
        
        self.assertEqual(result["time"], "2023-10-27T10:00:00")
        self.assertEqual(result["event"], "INFO")
        self.assertEqual(result["msg_id"], 5)
        self.assertEqual(result["msg_values"], '["123"]') # JSON string
        self.assertIsNone(result["value"])
        
        # Verify cache interaction
        self.mock_facade_instance.get_or_create_message_id.assert_called_with("INFO User {num} logged in")
        self.assertEqual(self.wp.msg_cache["INFO User {num} logged in"], 5)

    def test_prepare_entry_cached(self):
        """Test _prepare_entry uses local cache."""
        entry = {
            "time": "2023-10-27T10:00:00",
            "event": "INFO",
            "msg": "2023-10-27 10:00:00 INFO User 123 logged in",
            "value": None
        }
        
        # Pre-populate cache
        self.wp.msg_cache["INFO User {num} logged in"] = 10
        
        result = self.wp._prepare_entry(entry)
        
        self.assertEqual(result["msg_id"], 10)
        self.mock_facade_instance.get_or_create_message_id.assert_not_called()

    def test_process_queue_bulk_insert(self):
        """Test _process_queue calls bulk_insert_timeline_events."""
        q = queue.Queue()
        
        events = {"INFO": ["User 123 logged in"]}
        timeline = [
            {"time": "2023-10-27T10:00:00", "event": "INFO", "msg": "2023-10-27 10:00:00 INFO User 123 logged in", "value": None},
            {"time": "2023-10-27T10:00:01", "event": "INFO", "msg": "2023-10-27 10:00:01 INFO User 456 logged in", "value": None}
        ]
        q.put((events, timeline))
        
        self.mock_facade_instance.get_or_create_message_id.return_value = 1
        
        self.wp._process_queue(q)
        
        self.mock_facade_instance.bulk_insert_timeline_events.assert_called_once()
        call_args = self.mock_facade_instance.bulk_insert_timeline_events.call_args[0][0]
        self.assertEqual(len(call_args), 2)
        self.assertEqual(call_args[0]["msg_values"], '["123"]')
        self.assertEqual(call_args[1]["msg_values"], '["456"]')

    def test_process_queue_empty_item(self):
        """Test _process_queue handles None/empty item gracefully."""
        q = MagicMock()
        q.get.return_value = None # Simulate empty or None
import unittest
from unittest.mock import MagicMock, patch
import queue
import time
from src.writer_process import WriterProcess

class TestWriterProcess(unittest.TestCase):
    def setUp(self):
        # Patch the facade class where it is imported in writer_process
        self.facade_patcher = patch('src.writer_process.ChronoLogFacade')
        self.MockFacade = self.facade_patcher.start()
        self.mock_facade_instance = self.MockFacade.return_value
        
        # Initialize WriterProcess
        self.wp = WriterProcess(flush_interval=0.01)

    def tearDown(self):
        self.facade_patcher.stop()

    def test_init(self):
        """Test initialization of WriterProcess."""
        self.assertEqual(self.wp.flush_interval, 0.01)
        self.assertEqual(self.wp.facade, self.mock_facade_instance)
        self.assertEqual(self.wp.msg_cache, {})

    def test_prepare_entry_valid(self):
        """Test _prepare_entry with valid data."""
        entry = {
            "time": "2023-10-27T10:00:00",
            "event": "INFO",
            "msg": "2023-10-27 10:00:00 INFO User 123 logged in",
            "value": None
        }
        
        # Mock facade behavior
        self.mock_facade_instance.get_or_create_message_id.return_value = 5
        
        result = self.wp._prepare_entry(entry)
        
        self.assertEqual(result["time"], "2023-10-27T10:00:00")
        self.assertEqual(result["event"], "INFO")
        self.assertEqual(result["msg_id"], 5)
        self.assertEqual(result["msg_values"], '["123"]') # JSON string
        self.assertIsNone(result["value"])
        
        # Verify cache interaction
        self.mock_facade_instance.get_or_create_message_id.assert_called_with("INFO User {num} logged in")
        self.assertEqual(self.wp.msg_cache["INFO User {num} logged in"], 5)

    def test_prepare_entry_cached(self):
        """Test _prepare_entry uses local cache."""
        entry = {
            "time": "2023-10-27T10:00:00",
            "event": "INFO",
            "msg": "2023-10-27 10:00:00 INFO User 123 logged in",
            "value": None
        }
        
        # Pre-populate cache
        self.wp.msg_cache["INFO User {num} logged in"] = 10
        
        result = self.wp._prepare_entry(entry)
        
        self.assertEqual(result["msg_id"], 10)
        self.mock_facade_instance.get_or_create_message_id.assert_not_called()

    def test_process_queue_bulk_insert(self):
        """Test _process_queue calls bulk_insert_timeline_events."""
        q = queue.Queue()
        
        events = {"INFO": ["User 123 logged in"]}
        timeline = [
            {"time": "2023-10-27T10:00:00", "event": "INFO", "msg": "2023-10-27 10:00:00 INFO User 123 logged in", "value": None},
            {"time": "2023-10-27T10:00:01", "event": "INFO", "msg": "2023-10-27 10:00:01 INFO User 456 logged in", "value": None}
        ]
        q.put((events, timeline))
        
        self.mock_facade_instance.get_or_create_message_id.return_value = 1
        
        self.wp._process_queue(q)
        
        self.mock_facade_instance.bulk_insert_timeline_events.assert_called_once()
        call_args = self.mock_facade_instance.bulk_insert_timeline_events.call_args[0][0]
        self.assertEqual(len(call_args), 2)
        self.assertEqual(call_args[0]["msg_values"], '["123"]')
        self.assertEqual(call_args[1]["msg_values"], '["456"]')

    def test_process_queue_empty_item(self):
        """Test _process_queue handles None/empty item gracefully."""
        q = MagicMock()
        q.get.return_value = None # Simulate empty or None
        
        self.wp._process_queue(q)
        
        self.mock_facade_instance.bulk_insert_timeline_events.assert_not_called()

    def test_process_queue_exception(self):
        """Test _process_queue handles exceptions."""
        q = MagicMock()
        q.get.side_effect = Exception("Queue error")
        
        # Should not raise exception
        self.wp._process_queue(q)

if __name__ == "__main__":
    unittest.main()