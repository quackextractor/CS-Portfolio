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
        """Returns a new connection or reuses an existing one (if we were doing pooling manually, 
           but pyodbc handles pooling by default). 
           For simplicity in this singleton, we'll maintain one global connection object 
           or create a new one if it's closed.
           Actually, for multi-threaded apps (like Flask), it's often better to create a new connection per request 
           or use a proper pool. PyODBC manages pooling at the driver level.
           Let's return a new connection each time to be safe with threads, 
           relying on driver pooling."""
        return pyodbc.connect(self.connection_string)

    def execute_query(self, query, params=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()

    def execute_non_query(self, query, params=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()

    def execute_sp(self, sp_name, params=None):
        """
        Executes a stored procedure.
        params: list or tuple of parameters
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
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
