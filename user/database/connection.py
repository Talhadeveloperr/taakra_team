#user/database/connection.py
import pyodbc

class DatabaseConnection:
    def __init__(self, database_name: str):
        self.connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=DESKTOP-RTV4G1L\\SQLEXPRESS;"
            f"DATABASE={database_name};"
            "Trusted_Connection=yes;"
            "Encrypt=no;"
        )

    def get_connection(self):
        return pyodbc.connect(self.connection_string)