import re
from datetime import datetime
from config import KEY_VAL_RE, VAR_REGEX

class LogParser:
    def __init__(self, var_regex=None):
        self.var_regex = var_regex or VAR_REGEX
        self.key_val_re = KEY_VAL_RE

    def parse_lines(self, lines):
        events = {"ERROR": [], "WARNING": []}
        timeline = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            timestamp = self.extract_timestamp(line)
            self.parse_errors_warnings(line, timestamp, events, timeline)
            self.parse_variables(line, timestamp, events, timeline)

        return events, timeline

    def extract_timestamp(self, line):
        time_str = line.split(" ", 2)[:2]
        ts = " ".join(time_str)
        try:
            return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").isoformat()
        except Exception:
            return None

    def parse_errors_warnings(self, line, timestamp, events, timeline):
        if "ERROR" in line:
            self._add_event("ERROR", line, "error", timestamp, events, timeline)
        if "WARNING" in line:
            self._add_event("WARNING", line, "warning", timestamp, events, timeline)

    def parse_variables(self, line, timestamp, events, timeline):
        if self.var_regex:
            for var, rx in self.var_regex.items():
                m = rx.search(line)
                if m:
                    val = int(m.group(1))
                    self._add_event(var, line, var, timestamp, events, timeline, val)
        else:
            for m in self.key_val_re.finditer(line):
                key = m.group(1)
                val = int(m.group(2))
                if key.upper() in ("ERROR", "WARNING"):
                    continue
                self._add_event(key, line, key, timestamp, events, timeline, val)

    def _add_event(self, key, line, event_name, timestamp, events, timeline, value=None):
        events.setdefault(key, []).append(line)
        entry = {"time": timestamp, "event": event_name}
        if value is not None:
            entry["value"] = value
        else:
            entry["msg"] = line
        timeline.append(entry)