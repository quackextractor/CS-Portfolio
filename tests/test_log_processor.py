from log_processor import LogProcessor


class FakeQueue:
    def __init__(self):
        self.items = []
        self.put_calls = 0

    def put(self, item, timeout=None):
        # fail first two times, succeed on third
        self.put_calls += 1
        if self.put_calls < 3:
            raise Exception("full")
        self.items.append(item)


def test_safe_queue_put_retries_and_succeeds():
    lp = LogProcessor(input_file="unused", num_processes=1)
    # replace internal queue with a fake that raises first twice
    fake = FakeQueue()
    lp.queue = fake

    lp._safe_queue_put(("events", "timeline"))
    assert fake.put_calls >= 3
    assert fake.items and fake.items[0] == ("events", "timeline")
