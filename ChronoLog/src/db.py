import pyodbc
import os
import threading
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnectionError(Exception):
    pass

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
        
        self._ensure_database_exists()
        
        self._conn = None
        self._initialized = True

    def _ensure_database_exists(self):
        """
        Parses the connection string to find the target database,
        connects to 'master', checks if the target database exists,
        and creates it if it doesn't.
        """
        # Simple parsing to find DATABASE=... or Database=...
        # This assumes the connection string format is standard ODBC
        import re
        match = re.search(r"(?i)(?:DATABASE|Initial Catalog)\s*=\s*([^;]+)", self.connection_string)
        if not match:
            # If no database specified, nothing to create
            return
        
        target_db = match.group(1).strip()
        
        # Create a connection string for master
        # We replace the database part with 'master' or remove it and rely on default
        # Ideally, we explicitly connect to master.
        
        # Regex to replace the database part with 'master'
        master_conn_str = re.sub(r"(?i)(?:DATABASE|Initial Catalog)\s*=\s*[^;]+", "DATABASE=master", self.connection_string)
        
        # If the original string didn't have DATABASE, we might need to append it? 
        # But we only got here if we found it.
        
        try:
            # Connect to master
            # We use a fresh connection here, not self.get_connection() because self._conn isn't ready
            with pyodbc.connect(master_conn_str, autocommit=True) as conn:
                cursor = conn.cursor()
                
                # Check if DB exists
                # SQL Server specific check
                check_query = "SELECT name FROM sys.databases WHERE name = ?"
                cursor.execute(check_query, (target_db,))
                if not cursor.fetchone():
                    print(f"Database '{target_db}' does not exist. Creating...")
                    # CREATE DATABASE cannot run in a multi-statement transaction usually, 
                    # but autocommit=True helps.
                    # Parameterization for identifiers is not supported in standard SQL, 
                    # so we must be careful. Ideally validate target_db is safe.
                    # For this internal tool, we assume env var is safe-ish.
                    # But let's at least quote it.
                    cursor.execute(f"CREATE DATABASE [{target_db}]")
                    print(f"Database '{target_db}' created successfully.")
                else:
                    pass
                    # print(f"Database '{target_db}' already exists.")
                    
        except Exception as e:
            print(f"Warning: Could not ensure database '{target_db}' exists. Error: {e}")
            # We don't raise here because maybe the user doesn't have permissions 
            # but the DB exists, or some other issue. We let the main connection try.

    def get_connection(self):
        """
        Returns a connection. Reuses the existing connection if it's open.
        Raises DatabaseConnectionError if connection fails.
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

        try:
            self._conn = pyodbc.connect(self.connection_string)
            return self._conn
        except pyodbc.Error as e:
            raise DatabaseConnectionError(f"Failed to connect to database: {e}")

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
