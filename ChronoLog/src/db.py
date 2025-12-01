import pyodbc
import os
import threading
from dotenv import load_dotenv

load_dotenv()

class SQLConnection:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SQLConnection, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.connection_string = os.getenv("DB_CONNECTION_STRING")
        if not self.connection_string:
            raise ValueError("DB_CONNECTION_STRING environment variable not set")
        
        self._conn = None
        self._initialized = True

    def get_connection(self):
        """
        Returns a connection. Reuses the existing connection if it's open.
        """
        if self._conn:
            try:
                # Check if connection is still alive
                # This is a simple check; for production, a more robust pool is better.
                # But for this assignment, reusing the single connection is sufficient 
                # to fix the "new connection per query" issue.
                self._conn.cursor().execute("SELECT 1")
                return self._conn
            except Exception:
                # Connection might be closed or broken
                self._conn = None

        self._conn = pyodbc.connect(self.connection_string)
        return self._conn

    def execute_query(self, query, params=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            # Do not close conn here as we are reusing it

    def execute_non_query(self, query, params=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
        finally:
            cursor.close()

    def execute_sp(self, sp_name, params=None):
        """
        Executes a stored procedure.
        params: list or tuple of parameters
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Construct the SQL for SP call
            # Example: EXEC sp_name ?, ?
            if params:
                placeholders = ",".join(["?"] * len(params))
                sql = f"{{CALL {sp_name} ({placeholders})}}"
                cursor.execute(sql, params)
            else:
                sql = f"{{CALL {sp_name}}}"
                cursor.execute(sql)
            
            # Check if it returns rows
            if cursor.description:
                result = cursor.fetchall()
                conn.commit()
                return result
            
            conn.commit()
            return None
        finally:
            cursor.close()
