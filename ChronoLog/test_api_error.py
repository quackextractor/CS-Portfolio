import sys
import os
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.join(os.getcwd(), 'src'))

from db import DatabaseConnectionError
from api import app

class TestApiError(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    @patch('api.facade.get_timeseries')
    def test_database_error_handling(self, mock_get_timeseries):
        # Simulate a database connection error
        mock_get_timeseries.side_effect = DatabaseConnectionError("Connection failed")
        
        response = self.client.get('/api/timeseries?metric=test')
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.get_json()}")
        
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()['error'], 'Database unavailable')

if __name__ == '__main__':
    unittest.main()
