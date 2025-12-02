import unittest
import sys
import os
import re
import pyodbc
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'src'))

class TestDBCreation(unittest.TestCase):
    def setUp(self):
        # Load dotenv to get original connection string
        load_dotenv()
        self.original_conn_str = os.getenv("DB_CONNECTION_STRING")
        if not self.original_conn_str:
            self.skipTest("DB_CONNECTION_STRING not set")
            
        self.test_db_name = "ChronoLog_Test_Creation_12345"
        
        # Create test connection string
        # Check for DATABASE or Initial Catalog case-insensitively
        if re.search(r"(?i)DATABASE=", self.original_conn_str):
            self.test_conn_str = re.sub(r"(?i)DATABASE=[^;]+", f"DATABASE={self.test_db_name}", self.original_conn_str)
        elif re.search(r"(?i)Initial Catalog=", self.original_conn_str):
            self.test_conn_str = re.sub(r"(?i)Initial Catalog=[^;]+", f"Initial Catalog={self.test_db_name}", self.original_conn_str)
        else:
            self.test_conn_str = self.original_conn_str + f";DATABASE={self.test_db_name}"
            
        # Set environment variable for the test
        self.original_env_conn_str = os.environ.get("DB_CONNECTION_STRING")
        os.environ["DB_CONNECTION_STRING"] = self.test_conn_str

        # Reset singleton to force re-initialization
        from db import SQLConnection
        SQLConnection._instance = None

    def tearDown(self):
        # Restore environment variable
        if self.original_env_conn_str:
            os.environ["DB_CONNECTION_STRING"] = self.original_env_conn_str
        else:
            del os.environ["DB_CONNECTION_STRING"]
            
        # Drop the test database if it exists
        master_conn_str = re.sub(r"(?i)(?:DATABASE|Initial Catalog)\s*=\s*[^;]+", "DATABASE=master", self.original_conn_str)
        try:
            with pyodbc.connect(master_conn_str, autocommit=True) as conn:
                cursor = conn.cursor()
                cursor.execute(f"IF EXISTS (SELECT name FROM sys.databases WHERE name = '{self.test_db_name}') DROP DATABASE [{self.test_db_name}]")
        except Exception as e:
            print(f"Warning: Failed to cleanup test database: {e}")

    def test_db_creation(self):
        # Check if we have permissions to create database
        master_conn_str = re.sub(r"(?i)(?:DATABASE|Initial Catalog)\s*=\s*[^;]+", "DATABASE=master", self.original_conn_str)
        try:
            with pyodbc.connect(master_conn_str, autocommit=True) as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(f"CREATE DATABASE [{self.test_db_name}]")
                    cursor.execute(f"DROP DATABASE [{self.test_db_name}]")
                except pyodbc.Error as e:
                    # Check for permission denied error (42000)
                    # e.args is usually (sqlstate, message)
                    if len(e.args) > 0 and "42000" in e.args[0] and "permission denied" in str(e):
                        self.skipTest("Skipping test: No permission to create database.")
                    # Also check string representation just in case
                    elif "permission denied" in str(e).lower():
                        self.skipTest("Skipping test: No permission to create database.")
                    else:
                        print(f"Warning: Unexpected error during permission check: {e}")
                        # If we can't create it here, we probably can't create it in the test either
                        self.skipTest(f"Skipping test: Failed to create test database: {e}")
        except Exception as e:
             if "permission denied" in str(e).lower():
                self.skipTest("Skipping test: No permission to create database.")
             print(f"Warning during permission check: {e}")
             # If we can't connect to master or something else fails, we probably can't run the test
             self.skipTest(f"Skipping test: Error during setup: {e}")

        try:
            from db import SQLConnection
            
            # Initialize connection - this should trigger creation
            print("Initializing SQLConnection...")
            db = SQLConnection()
            
            # Verify database exists
            print("Verifying database existence...")
            
            with pyodbc.connect(master_conn_str, autocommit=True) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sys.databases WHERE name = ?", (self.test_db_name,))
                if not cursor.fetchone():
                    self.fail(f"Database '{self.test_db_name}' was NOT created.")
                else:
                    print(f"SUCCESS: Database '{self.test_db_name}' exists!")
                    
        except Exception as e:
            self.fail(f"An error occurred: {e}")

if __name__ == '__main__':
    unittest.main()
