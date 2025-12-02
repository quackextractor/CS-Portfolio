import os
import sys
import pyodbc
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from db import SQLConnection

def test_connection_failure():
    print("Testing connection failure...")
    
    # Set a dummy connection string
    os.environ['DB_CONNECTION_STRING'] = 'DRIVER={SQL Server};SERVER=invalid_server;DATABASE=db;UID=user;PWD=pass'
    
    # Mock pyodbc.connect to raise an exception
    with patch('pyodbc.connect', side_effect=pyodbc.Error("Connection failed")):
        try:
            db = SQLConnection()
            print("SQLConnection initialized.")
            
            # This should raise pyodbc.Error, not AttributeError
            db.execute_sp("sp_GetTimeseries", ("metric", 100))
            
        except AttributeError as e:
            print(f"FAILED: Still getting AttributeError: {e}")
        except pyodbc.Error as e:
            print(f"FAILED: Caught raw pyodbc.Error: {e}")
        except Exception as e:
            if type(e).__name__ == 'DatabaseConnectionError':
                print("SUCCESS: Caught DatabaseConnectionError as expected.")
            else:
                print(f"Caught unexpected exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_connection_failure()
