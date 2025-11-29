import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from facade import ChronoLogFacade

def test_messages():
    print("Testing get_messages...")
    facade = ChronoLogFacade()
    
    try:
        msgs = facade.get_messages()
        print(f"Messages: {json.dumps(msgs, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_messages()
