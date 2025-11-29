import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from db import SQLConnection

def count_rows():
    print("Counting rows...")
    db = SQLConnection()
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM TimelineEvents")
        count = cursor.fetchone()[0]
        print(f"TimelineEvents count: {count}")
        
        cursor.execute("SELECT COUNT(*) FROM Messages")
        msg_count = cursor.fetchone()[0]
        print(f"Messages count: {msg_count}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    count_rows()
