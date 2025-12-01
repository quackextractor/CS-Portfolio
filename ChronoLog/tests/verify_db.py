import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'src'))

try:
    from db import SQLConnection
    print("Attempting to connect to database...")
    db = SQLConnection()
    conn = db.get_connection()
    print("Successfully connected to database!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT @@VERSION")
    row = cursor.fetchone()
    print(f"SQL Server Version: {row[0]}")
    
    conn.close()
    
except Exception as e:
    print(f"Failed to connect: {e}")
    print("Please check your .env file and ensure SQL Server is running.")
