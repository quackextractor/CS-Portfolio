import sys
import os
import re
import pyodbc
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'src'))

# We need to load dotenv manually first to get the original connection string
from dotenv import load_dotenv
load_dotenv()

original_conn_str = os.getenv("DB_CONNECTION_STRING")
if not original_conn_str:
    print("Skipping test: DB_CONNECTION_STRING not set")
    sys.exit(0)

# Generate a unique test database name
TEST_DB_NAME = "ChronoLog_Test_Creation_12345"

# Replace database name in connection string
# Regex to replace DATABASE=... or Initial Catalog=...
# We assume the connection string has one of these.
if "DATABASE=" in original_conn_str:
    test_conn_str = re.sub(r"DATABASE=[^;]+", f"DATABASE={TEST_DB_NAME}", original_conn_str)
elif "Initial Catalog=" in original_conn_str:
    test_conn_str = re.sub(r"Initial Catalog=[^;]+", f"Initial Catalog={TEST_DB_NAME}", original_conn_str)
else:
    # Append it if missing (though the code assumes it's there to replace)
    test_conn_str = original_conn_str + f";DATABASE={TEST_DB_NAME}"

# Set the environment variable BEFORE importing db (or re-importing)
# But db.py calls load_dotenv() at module level. 
# load_dotenv(override=False) is default, so setting os.environ here should work.
os.environ["DB_CONNECTION_STRING"] = test_conn_str

print(f"Testing with connection string: {test_conn_str}")

try:
    from db import SQLConnection
    
    # Initialize connection - this should trigger creation
    print("Initializing SQLConnection...")
    db = SQLConnection()
    
    # Verify database exists
    print("Verifying database existence...")
    # We can use the same logic as in the class, or just try to connect to it.
    
    # Let's connect to master and check
    master_conn_str = re.sub(r"(?i)(?:DATABASE|Initial Catalog)\s*=\s*[^;]+", "DATABASE=master", original_conn_str)
    
    with pyodbc.connect(master_conn_str, autocommit=True) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sys.databases WHERE name = ?", (TEST_DB_NAME,))
        if cursor.fetchone():
            print(f"SUCCESS: Database '{TEST_DB_NAME}' exists!")
        else:
            print(f"FAILURE: Database '{TEST_DB_NAME}' was NOT created.")
            sys.exit(1)
            
        # Cleanup
        print("Cleaning up...")
        cursor.execute(f"DROP DATABASE [{TEST_DB_NAME}]")
        print("Database dropped.")

except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
