from flask import Flask, send_from_directory, jsonify, request, abort
import os, json, math

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_FILE = os.path.join(BASE_DIR, "output", "output.json")
SUMMARY_FILE = os.path.join(BASE_DIR, "output", "output.json.summary.json")
PUBLIC_DIR = os.path.join(BASE_DIR, "vendor", "frontend_demo", "public")

@app.route('/')
def index():
    return send_from_directory(PUBLIC_DIR, "index.html")

@app.route('/summary')
def summary():
    if not os.path.exists(SUMMARY_FILE):
        return jsonify({}), 404
    with open(SUMMARY_FILE, 'r', encoding='utf-8') as f:
        return jsonify(json.load(f))

@app.route('/messages')
def messages():
    """
    Return templates map { id: template } by scanning file once.
    """
    templates = {}
    if not os.path.exists(OUTPUT_FILE):
        return jsonify(templates)
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                obj = json.loads(line)
                if "template" in obj and "id" in obj:
                    templates[int(obj["id"])] = obj["template"]
            except Exception:
                continue
    return jsonify(templates)

@app.route('/timeline')
def timeline_page():
    """
    Paginate by *events only* (skip template lines).
    Query params:
      - page (1-based, default 1)
      - per_page (default 30)
    Returns list of event objects.
    """
    page = max(1, int(request.args.get('page', 1)))
    per_page = max(1, int(request.args.get('per_page', 30)))
    start_idx = (page - 1) * per_page
    end_idx = page * per_page

    if not os.path.exists(OUTPUT_FILE):
        return jsonify([])

    result = []
    seen = 0  # count of non-template events encountered
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                obj = json.loads(line)
            except Exception:
                continue
            # skip template definitions
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
    Return latest N points for a numeric metric (e.g. metric=latency).
    Query params:
      - metric (default: latency)
      - limit (default: 500)
    Returns array of {time, value}.
    """
    metric = request.args.get('metric', 'latency')
    limit = max(1, min(5000, int(request.args.get('limit', 500))))

    if not os.path.exists(OUTPUT_FILE):
        return jsonify([])

    points = []
    # collect matching events (value present and event==metric or event name equals metric)
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if "template" in obj:
                continue
            # numeric metric stored in "value"
            if "value" in obj and (obj.get("event") == metric or obj.get("event").lower() == metric.lower()):
                points.append({"time": obj.get("time"), "value": obj.get("value")})
    # keep last `limit` points
    if len(points) > limit:
        points = points[-limit:]
    return jsonify(points)

if __name__ == "__main__":
    # debug allowed for local dev only
    app.run(debug=True, port=8000)
