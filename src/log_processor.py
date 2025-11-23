import multiprocessing
import os
import time
import json
import hashlib
import pickle

# TODO add auto variable tracking

# Config from .env or defaults
INPUT_FILE_PATH = os.getenv("INPUT_FILE_PATH", "../examples/sample.log")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "50000"))
QUEUE_MAX_SIZE = int(os.getenv("QUEUE_MAX_SIZE", "100"))
STATE_FILE = os.getenv("STATE_FILE", "../state/parser_state.json")
SEEN_FILE = os.getenv("SEEN_FILE", "../state/seen_lines.pkl")
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "0.5"))
NUM_PROCESSES = int(os.getenv("NUM_PROCESSES", "3"))
STATE_SAVE_INTERVAL = 5

def save_state(position, seen_lines):
    tmp_state = STATE_FILE + ".tmp"
    tmp_seen = SEEN_FILE + ".tmp"
    with open(tmp_state, "w") as f:
        json.dump({"position": position}, f)
    with open(tmp_seen, "wb") as f:
        pickle.dump(seen_lines, f)
    os.replace(tmp_state, STATE_FILE)
    os.replace(tmp_seen, SEEN_FILE)

def load_state():
    position = 0
    seen_lines = set()
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            try:
                position = json.load(f).get("position", 0)
            except json.JSONDecodeError:
                position = 0
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "rb") as f:
            try:
                seen_lines = pickle.load(f)
            except Exception:
                seen_lines = set()
    return position, seen_lines

def parse_lines_worker(lines, queue, stop_flag):
    if stop_flag.is_set():
        return
    events = {"ERROR": [], "WARNING": [], "latency": []}
    for line in lines:
        line = line.strip()
        for key in events:
            if key in line:
                events[key].append(line)
    queue.put(events)

def chunked_file_reader(file_path, start_pos=0, chunk_size=CHUNK_SIZE):
    with open(file_path, "r") as f:
        f.seek(start_pos)
        while True:
            chunk = []
            for _ in range(chunk_size):
                line = f.readline()
                if not line:
                    break
                chunk.append(line)
            if chunk:
                yield chunk, f.tell()
            else:
                current_size = os.path.getsize(file_path)
                if current_size < f.tell():
                    f.seek(0)
                    yield [], 0
                else:
                    time.sleep(POLL_INTERVAL)

def live_parse(number_of_processes):
    queue = multiprocessing.Queue(maxsize=QUEUE_MAX_SIZE)
    stop_flag = multiprocessing.Event()
    pool = multiprocessing.Pool(number_of_processes)

    merged = {"ERROR": [], "WARNING": [], "latency": []}
    last_position, seen_lines = load_state()
    last_state_save = time.time()

    try:
        for chunk, new_pos in chunked_file_reader(INPUT_FILE_PATH, start_pos=last_position):
            if chunk:
                pool.apply_async(parse_lines_worker, args=(chunk, queue, stop_flag))
                last_position = new_pos

            while not queue.empty():
                result = queue.get()
                for key in merged:
                    for line in result[key]:
                        h = hashlib.md5(line.encode()).hexdigest()
                        if h not in seen_lines:
                            seen_lines.add(h)
                            merged[key].append(line)

            now = time.time()
            if now - last_state_save >= STATE_SAVE_INTERVAL:
                save_state(last_position, seen_lines)
                last_state_save = now

    except KeyboardInterrupt:
        stop_flag.set()
    finally:
        pool.close()
        pool.join()

        while not queue.empty():
            result = queue.get()
            for key in merged:
                for line in result[key]:
                    h = hashlib.md5(line.encode()).hexdigest()
                    if h not in seen_lines:
                        seen_lines.add(h)
                        merged[key].append(line)

        save_state(last_position, seen_lines)

    return merged

if __name__ == "__main__":
    result = live_parse(NUM_PROCESSES)
    print(result)
