import time
import re
import json
import os
import queue
from facade import ChronoLogFacade
from config import WRITER_FLUSH_INTERVAL

class WriterProcess:
    def __init__(self, flush_interval=WRITER_FLUSH_INTERVAL):
        self.flush_interval = flush_interval
        self.facade = ChronoLogFacade()
        self.msg_cache = {} 

    def run(self, queue, stop_flag):
        print(f"WriterProcess started. PID: {os.getpid()}")
        try:
            while not stop_flag.is_set() or not queue.empty():
                self._process_queue(queue)
        except KeyboardInterrupt:
            print("WriterProcess interrupted")
        except Exception as e:
            print(f"WriterProcess crashed: {e}")
        finally:
            print("WriterProcess draining queue...")
            while not queue.empty():
                self._process_queue(queue)
            print("WriterProcess finished")

    def _process_queue(self, queue_obj):
        try:
            item = queue_obj.get(timeout=0.5)
            if not item:
                return
                
            delta_events, delta_timeline = item
            print(f"Writer received chunk with {len(delta_timeline)} events") # DEBUG
            
            bulk_data = []
            for entry in delta_timeline:
                processed = self._prepare_entry(entry)
                if processed:
                    bulk_data.append(processed)
            
            if bulk_data:
                print(f"Bulk inserting {len(bulk_data)} events") # DEBUG
                self.facade.bulk_insert_timeline_events(bulk_data)
            else:
                # pass
                print("No data to insert") # DEBUG

        except queue.Empty:
            print("Writer queue empty, waiting...") # DEBUG
            pass
        except Exception as e:
            print(f"Writer error: {e}") # DEBUG
            pass

    def _prepare_entry(self, entry):
        msg_key = entry.get("msg")
        msg_id = None
        msg_values = None

        if msg_key:
            stripped = re.sub(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} ", "", msg_key)
            nums = re.findall(r"\b\d+\b", stripped)
            tmpl = re.sub(r"\b\d+\b", "{num}", stripped)

            # Check local cache first
            msg_id = self.msg_cache.get(tmpl)
            if msg_id is None:
                # Get from DB (or create)
                msg_id = self.facade.get_or_create_message_id(tmpl)
                if msg_id is not None:
                    msg_id = int(msg_id)
                    self.msg_cache[tmpl] = msg_id

            if nums:
                msg_values = json.dumps(nums)

        return {
            "time": entry["time"],
            "event": entry["event"],
            "msg_id": msg_id,
            "msg_values": msg_values,
            "value": str(entry.get("value")) if entry.get("value") is not None else None
        }