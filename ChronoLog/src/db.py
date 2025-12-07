import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnectionError(Exception):
    pass

class SQLConnection:
    def __init__(self):
        self.connection_string = os.getenv("DB_CONNECTION_STRING")
        if not self.connection_string:
            raise ValueError("DB_CONNECTION_STRING environment variable not set")
        
        self._ensure_database_exists()

    def _ensure_database_exists(self):
        """
        Parses the connection string to find the target database,
        connects to 'master', checks if the target database exists,
        and creates it if it doesn't.
        """
        import re
        match = re.search(r"(?i)(?:DATABASE|Initial Catalog)\s*=\s*([^;]+)", self.connection_string)
        if not match:
            return
        
        target_db = match.group(1).strip()
        master_conn_str = re.sub(r"(?i)(?:DATABASE|Initial Catalog)\s*=\s*[^;]+", "DATABASE=master", self.connection_string)
        
        try:
            conn = pyodbc.connect(master_conn_str, autocommit=True)
            cursor = conn.cursor()
            try:
                check_query = "SELECT name FROM sys.databases WHERE name = ?"
                cursor.execute(check_query, (target_db,))
                if not cursor.fetchone():
                    print(f"Database '{target_db}' does not exist. Creating...")
                    cursor.execute(f"CREATE DATABASE [{target_db}]")
                    print(f"Database '{target_db}' created successfully.")
            finally:
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"Warning: Could not ensure database '{target_db}' exists. Error: {e}")

    def get_connection(self):
        """
        Returns a new connection.
        """
        try:
            return pyodbc.connect(self.connection_string)
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
            conn.close()

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
            conn.close()

    def execute_sp(self, sp_name, params=None):
        """
        Executes a stored procedure.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                placeholders = ",".join(["?"] * len(params))
                sql = f"{{CALL {sp_name} ({placeholders})}}"
                cursor.execute(sql, params)
            else:
                sql = f"{{CALL {sp_name}}}"
                cursor.execute(sql)
            
            if cursor.description:
                result = cursor.fetchall()
                conn.commit()
                return result
            
            conn.commit()
            return None
        finally:
            cursor.close()
            conn.close()
