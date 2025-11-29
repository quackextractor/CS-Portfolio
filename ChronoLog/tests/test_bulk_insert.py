import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from facade import ChronoLogFacade

def test_bulk_insert():
    print("Testing bulk insert...")
    facade = ChronoLogFacade()
    
    # Create some dummy events
    events = [
        {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": "test_event",
            "msg_id": None,
            "msg_values": None,
            "value": "123.45"
        },
        {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": "test_event_2",
            "msg_id": None,
            "msg_values": None,
            "value": "678.90"
        }
    ]
    
    try:
        print(f"Inserting {len(events)} events...")
        facade.bulk_insert_timeline_events(events)
        print("Insert called.")
        
        # Verify
        print("Verifying...")
        db = facade.db
        rows = db.execute_query("SELECT TOP 5 * FROM TimelineEvents ORDER BY EventId DESC")
        for row in rows:
            print(row)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_bulk_insert()
