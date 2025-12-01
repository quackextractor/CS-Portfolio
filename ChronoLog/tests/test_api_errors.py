import sys
import os
import json
import unittest
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from api import app, facade

class TestApiErrors(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_timeseries_missing_metric(self):
        response = self.app.get('/api/timeseries')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), {"error": "Metric parameter is required"})

    def test_get_summary_empty(self):
        original_get_summary = facade.get_summary
        facade.get_summary = MagicMock(return_value={})
        try:
            response = self.app.get('/api/summary')
            self.assertEqual(response.status_code, 404)
            self.assertEqual(json.loads(response.data), {"error": "Summary data not available"})
        finally:
            facade.get_summary = original_get_summary

    def test_404_handler(self):
        response = self.app.get('/api/nonexistent_endpoint')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.data), {"error": "Not found"})

if __name__ == '__main__':
    unittest.main()
