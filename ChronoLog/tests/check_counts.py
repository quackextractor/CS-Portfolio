import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from db import SQLConnection
from facade import ChronoLogFacade

def check_counts():
    print("Checking counts...")
    db = SQLConnection()
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        # Direct query
        cursor.execute("SELECT COUNT(*) FROM TimelineEvents WHERE EventType = 'error'")
        errors = cursor.fetchone()[0]
        print(f"DB Error Count: {errors}")
        
        cursor.execute("SELECT COUNT(*) FROM TimelineEvents WHERE EventType = 'warning'")
        warnings = cursor.fetchone()[0]
        print(f"DB Warning Count: {warnings}")
        
        # Facade call (uses SP)
        facade = ChronoLogFacade()
        summary = facade.get_summary()
        print(f"API Summary: {summary}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_counts()
