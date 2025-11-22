import multiprocessing

stop_flag = multiprocessing.Event()  # IMPORTANT!!!!
shared_result = None
result_lock = multiprocessing.Lock()

events = {'ERROR': [], 'WARNING': [], 'latency': []}
input_file_path = "../examples/sample.log"

def parse_log(from_line=0, to_line=None):
    with open(input_file_path, 'r') as f:
        for i, line in enumerate(f):
            if stop_flag.is_set():
                return None
            if i < from_line:
                continue
            if to_line is not None and i >= to_line:
                break
            line = line.strip()
            for key in events:
                if key in line:
                    events[key].append(line)
    return events


class ParseProcess(multiprocessing.Process):
    def __init__(self, from_line, to_line):
        super().__init__()
        self.from_line = from_line
        self.to_line = to_line
        self.result = None

    def run(self):
        global shared_result
        if stop_flag.is_set():
            return
        r = parse_log(self.from_line, self.to_line)
        if r is not None:
            with result_lock: # gate that locks after entering, only one Thread can get in at a time. With ensures it unlocks on Error
                if shared_result is None:
                    pass
                    # TODO add merge logic??
        self.result = r

def count_lines(file_path):
    with open(file_path, 'r') as f:
        return sum(1 for _ in f)

def parse_parallel(number_of_processes, total_lines):
    processes = []
    chunk = total_lines / number_of_processes

    for i in range(number_of_processes):
        t = ParseProcess(i * chunk, (i + 1) * chunk)
        processes.append(t)

    for t in processes:
        t.start()

    for t in processes:
        t.join()

    return shared_result

if __name__ == '__main__':
    total_lines = count_lines(input_file_path)
    parse_parallel(3, total_lines)
