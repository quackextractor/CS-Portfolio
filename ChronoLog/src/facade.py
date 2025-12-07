import json
from db import SQLConnection

class ChronoLogFacade:
    def __init__(self):
        self.db = SQLConnection()

    def get_messages(self):
        """
        Retrieves all message templates.
        Returns a dict {id: template}
        """
        rows = self.db.execute_query("SELECT MessageId, Template FROM Messages")
        return {str(row.MessageId): row.Template for row in rows}

    def get_or_create_message_id(self, template):
        """
        Gets existing message ID or creates a new one.
        """
        rows = self.db.execute_sp("sp_GetOrInsertMessage", (template,))
        if rows:
            return rows[0].MessageId
        return None

    def insert_timeline_event(self, event_time, event_type, message_id=None, message_values=None, value=None):
        """
        Inserts a timeline event.
        message_values should be a list of strings/numbers, which will be converted to JSON.
        """
        msg_values_json = json.dumps(message_values) if message_values else None
        
        # Ensure value is float or None
        val = float(value) if value is not None else None

        self.db.execute_sp("sp_InsertTimelineEvent", (
            event_time, 
            event_type, 
            message_id, 
            msg_values_json, 
            val
        ))

    def bulk_insert_timeline_events(self, events):
        """
        Bulk inserts timeline events.
        events: list of dicts with keys: time, event, msg_id, msg_values, value
        """
        if not events:
            return
            
        # Convert list of dicts to JSON string
        events_json = json.dumps(events)
        self.db.execute_sp("sp_BulkInsertTimelineEvents", (events_json,))

    def get_timeline_page(self, page=1, per_page=30, event_type=None):
        """
        Retrieves a page of timeline events.
        Returns a list of dictionaries.
        """
        rows = self.db.execute_sp("sp_GetTimelinePage", (page, per_page, event_type))
        if not rows:
            return []
        
        # Convert rows to dicts
        # Columns: EventId, time, event, msg_id, msg_values, value, template, TotalCount
        result = []
        for row in rows:
            result.append({
                "id": row.EventId,
                "time": row.time, # datetime object
                "event": row.event,
                "msg_id": row.msg_id,
                "msg_values": json.loads(row.msg_values) if row.msg_values else None,
                "value": float(row.value) if row.value is not None else None,
                "template": row.template,
                "total_count": row.TotalCount
            })
        return result

    def get_summary(self):
        """
        Retrieves summary statistics.
        """
        rows = self.db.execute_sp("sp_GetSummary")
        if not rows:
            return {}
        
        row = rows[0]
        return {
            "error_count": row.error_count,
            "warning_count": row.warning_count,
            "timeline_count": row.timeline_count,
            "unique_messages": row.unique_messages,
            "latency_metrics": {
                "count": row.latency_count,
                "average": float(row.latency_average) if row.latency_average is not None else 0
            }
        }

    def get_timeseries(self, metric, limit=500):
        """
        Retrieves timeseries data for a metric.
        """
        rows = self.db.execute_sp("sp_GetTimeseries", (metric, limit))
        if not rows:
            return []
        
        return [{"time": row.time, "value": float(row.value)} for row in rows]
