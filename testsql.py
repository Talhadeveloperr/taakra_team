# test.py
from user.database.connection import DatabaseConnection

def test_db_connection():
    # Replace 'YourDatabaseName' with your actual DB name
    db_name = "u11111" 
    db = DatabaseConnection(db_name)

    print(f"--- Attempting to connect to {db_name} ---")

    try:
        # 1. Establish connection
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # 2. Run a simple system query
        # This confirms we can not only connect but also execute SQL
        cursor.execute("SELECT @@VERSION AS Version, DB_NAME() AS CurrentDB")
        row = cursor.fetchone()

        if row:
            print("✅ Connection Successful!")
            print("-" * 30)
            print(f"Connected to: {row.CurrentDB}")
            print(f"SQL Server Version:\n{row.Version}")
            print("-" * 30)

        # 3. Clean up
        cursor.close()
        conn.close()
        print("🔌 Connection closed safely.")

    except Exception as error:
        print("❌ Test Failed!")
        print(f"Error details: {error}")

if __name__ == "__main__":
    test_db_connection()