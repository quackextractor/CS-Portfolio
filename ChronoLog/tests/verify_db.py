import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

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
