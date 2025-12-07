import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from facade import ChronoLogFacade

def verify():
    try:
        facade = ChronoLogFacade()
        
        print("Fetching all events...")
        all_events = facade.get_timeline_page(page=1, per_page=10)
        print(f"Found {len(all_events)} events (page 1).")
        if all_events:
            print(f"First event type: {all_events[0]['event']}")
            print(f"Total count (all): {all_events[0]['total_count']}")
        
        print("\nFetching errors...")
        errors = facade.get_timeline_page(page=1, per_page=10, event_type='error')
        print(f"Found {len(errors)} error events.")
        if errors:
            print(f"Total count (errors): {errors[0]['total_count']}")
            for e in errors:
                if e['event'] != 'error':
                    print(f"FAIL: Event type is {e['event']}")
                    return
            print("OK: All returned events are errors.")
        else:
            print("No errors found, so cannot verify filtering, but query ran successfully.")
        
        print("\nFetching warnings...")
        warnings = facade.get_timeline_page(page=1, per_page=10, event_type='warning')
        print(f"Found {len(warnings)} warning events.")
        if warnings:
            print(f"Total count (warnings): {warnings[0]['total_count']}")
            for w in warnings:
                if w['event'] != 'warning':
                    print(f"FAIL: Event type is {w['event']}")
                    return
            print("OK: All returned events are warnings.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify()
