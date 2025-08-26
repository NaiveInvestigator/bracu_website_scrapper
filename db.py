import mysql.connector

class MySQLDatabase:
    def __init__(self, host="localhost", user="root", password="", database=None):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database
        }
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        """Initialize connection and cursor."""
        if self.conn is None or not self.conn.is_connected():
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor()

    def execute(self, query, params=None, commit=True):
        """Execute a query with optional parameters."""
        self.connect()
        self.cursor.execute(query, params or ())
        if commit:
            self.conn.commit()
        return self.cursor

    def fetchone(self, query, params=None):
        self.execute(query, params, commit=False)
        return self.cursor.fetchone()

    def fetchall(self, query, params=None):
        self.execute(query, params, commit=False)
        return self.cursor.fetchall()

    def exists(self, table, column, value):
        result = self.fetchone(f"SELECT 1 FROM {table} WHERE {column}=%s LIMIT 1", (value,))
        return result is not None

    def insert(self, table, data):
        """Insert a dictionary into a table."""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        values = tuple(data.values())
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.execute(query, values)

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

