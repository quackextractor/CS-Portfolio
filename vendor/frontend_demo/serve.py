from flask import Flask, send_from_directory, jsonify, request
import os, json

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MESSAGES_FILE = os.path.join(BASE_DIR, "output", "messages.json")
TIMELINE_FILE = os.path.join(BASE_DIR, "output", "timeline.jsonl")
SUMMARY_FILE = os.path.join(BASE_DIR, "output", "summary.json")
PUBLIC_DIR = os.path.join(BASE_DIR, "vendor", "frontend_demo", "public")

@app.route('/')
def index():
    return send_from_directory(PUBLIC_DIR, "index.html")

@app.route('/summary')
def summary():
    if not os.path.exists(SUMMARY_FILE):
        return jsonify({}), 404
    with open(SUMMARY_FILE, 'r', encoding='utf-8') as f:
        try:
            return jsonify(json.load(f))
        except Exception:
            return jsonify({}), 500

@app.route('/messages')
def messages():
    if not os.path.exists(MESSAGES_FILE):
        return jsonify({})

    try:
        with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
            objs = json.load(f)  # load full array
        templates = {str(obj["id"]): obj["template"] for obj in objs if "id" in obj and "template" in obj}
        return jsonify(templates)
    except Exception:
        return jsonify({}), 500

@app.route('/timeline')
def timeline_page():
    page = max(1, int(request.args.get('page', 1)))
    per_page = max(1, int(request.args.get('per_page', 30)))
    start_idx = (page - 1) * per_page
    end_idx = page * per_page

    if not os.path.exists(TIMELINE_FILE):
        return jsonify([])

    result = []
    seen = 0
    with open(TIMELINE_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            # skip template definitions if any (messages file should hold those)
            if "template" in obj:
                continue
            # this is an event row
            if seen >= start_idx and seen < end_idx:
                result.append(obj)
            seen += 1
            if seen >= end_idx:
                break

    return jsonify(result)

@app.route('/timeseries')
def timeseries():
    """
    Supported metric values:
      - latency          => collects events where event == 'latency' and 'value' present
      - msg_<id>         => collects events where msg_id == <id> and msg_values present (takes first msg_value)
      - any event name   => if event matches and contains 'value' or 'msg_values' (first) it will be used
    Returns list of {time, value}
    """
    metric = request.args.get('metric', 'latency')
    limit = max(1, min(5000, int(request.args.get('limit', 500))))

    if not os.path.exists(TIMELINE_FILE):
        return jsonify([])

    points = []
    try:
        # try to detect msg_<id>
        msg_id = None
        if metric.startswith('msg_'):
            try:
                msg_id = int(metric.split('_', 1)[1])
            except Exception:
                msg_id = None

        with open(TIMELINE_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue

                # latency metric
                if metric.lower() == 'latency':
                    if obj.get('event', '').lower() == 'latency' and 'value' in obj:
                        try:
                            v = float(obj.get('value'))
                        except Exception:
                            v = obj.get('value')
                        points.append({"time": obj.get("time"), "value": v})
                    continue

                # explicit msg_<id>
                if msg_id is not None:
                    if obj.get('msg_id') == msg_id and isinstance(obj.get('msg_values'), list) and len(obj.get('msg_values')) > 0:
                        first = obj.get('msg_values')[0]
                        # try parse numeric
                        try:
                            v = float(first)
                        except Exception:
                            # not numeric, skip
                            continue
                        points.append({"time": obj.get("time"), "value": v})
                    continue

                # fallback: match by event name
                if obj.get('event', '').lower() == metric.lower():
                    if 'value' in obj:
                        try:
                            v = float(obj.get('value'))
                        except Exception:
                            v = obj.get('value')
                        points.append({"time": obj.get("time"), "value": v})
                    elif isinstance(obj.get('msg_values'), list) and len(obj.get('msg_values')) > 0:
                        first = obj.get('msg_values')[0]
                        try:
                            v = float(first)
                        except Exception:
                            continue
                        points.append({"time": obj.get("time"), "value": v})
                    # else ignore non-numeric
    except Exception:
        return jsonify([])

    if len(points) > limit:
        points = points[-limit:]
    return jsonify(points)

if __name__ == "__main__":
    app.run(debug=True, port=8000)
