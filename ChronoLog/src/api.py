from flask import Flask, jsonify, request, send_from_directory
from flasgger import Swagger
from facade import ChronoLogFacade

app = Flask(__name__)
swagger = Swagger(app)
facade = ChronoLogFacade()


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.route('/api/summary', methods=['GET'])
def get_summary():
    """
    Get summary statistics
    ---
    tags:
      - Dashboard
    responses:
      200:
        description: Summary statistics
        schema:
          type: object
          properties:
            error_count:
              type: integer
            warning_count:
              type: integer
            timeline_count:
              type: integer
            unique_messages:
              type: integer
            latency_metrics:
              type: object
              properties:
                count:
                  type: integer
                average:
                  type: number
    """
    data = facade.get_summary()
    if not data:
        return jsonify({"error": "Summary data not available"}), 404
    return jsonify(data)

@app.route('/api/timeline', methods=['GET'])
def get_timeline():
    """
    Get paginated timeline events
    ---
    tags:
      - Timeline
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: Page number
      - name: per_page
        in: query
        type: integer
        default: 30
        description: Items per page
    responses:
      200:
        description: List of timeline events
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              time:
                type: string
              event:
                type: string
              msg_id:
                type: integer
              msg_values:
                type: array
                items:
                  type: string
              value:
                type: number
              template:
                type: string
              total_count:
                type: integer
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)
    data = facade.get_timeline_page(page, per_page)
    return jsonify(data)

@app.route('/api/timeseries', methods=['GET'])
def get_timeseries():
    """
    Get timeseries data for a metric
    ---
    tags:
      - Metrics
    parameters:
      - name: metric
        in: query
        type: string
        required: true
        description: Metric name (e.g., 'latency', 'msg_0')
      - name: limit
        in: query
        type: integer
        default: 500
        description: Max points to return
    responses:
      200:
        description: Timeseries data
        schema:
          type: array
          items:
            type: object
            properties:
              time:
                type: string
              value:
                type: number
    """
    metric = request.args.get('metric')
    limit = request.args.get('limit', 500, type=int)
    
    if not metric:
        return jsonify({"error": "Metric parameter is required"}), 400
        
    data = facade.get_timeseries(metric, limit)
    if not data:
        return jsonify({"error": f"No data found for metric: {metric}"}), 404
    return jsonify(data)

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """
    Get all message templates
    ---
    tags:
      - Messages
    responses:
      200:
        description: Map of message IDs to templates
        schema:
          type: object
          additionalProperties:
            type: string
    """
    data = facade.get_messages()
    return jsonify(data)

@app.route('/')
def index():
    return send_from_directory('../vendor/frontend_demo/public', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
