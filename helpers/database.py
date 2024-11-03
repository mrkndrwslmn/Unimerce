import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Establish and return a database connection."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='unimerce'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def execute_query(query, params=(), fetch_all=True):
    """
    Executes a SQL query with optional parameters.
    
    Args:
        query (str): The SQL query to be executed.
        params (tuple): Optional parameters for the SQL query.
        fetch_all (bool): Whether to fetch all results (True) or a single result (False).
    
    Returns:
        list or dict or None: Query results or None if an error occurs.
    """
    conn = get_db_connection()
    if not conn:
        print("Failed to establish a database connection.")
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        if query.strip().lower().startswith("select"):
            return cursor.fetchall() if fetch_all else cursor.fetchone()
        else:
            conn.commit()  # Commit for INSERT, UPDATE, DELETE operations
            return cursor.lastrowid if cursor.lastrowid else None
    except Error as e:
        print(f"Error executing query: {e}")
        conn.rollback()  # Rollback in case of an error
        return None
    finally:
        cursor.close()
        conn.close()

def execute_transaction(queries):
    """
    Executes multiple queries as a single transaction.
    
    Args:
        queries (list of tuples): Each tuple contains (query, params).
    
    Returns:
        bool: True if the transaction is successful, False otherwise.
    """
    conn = get_db_connection()
    if not conn:
        print("Failed to establish a database connection.")
        return False

    try:
        cursor = conn.cursor()
        for query, params in queries:
            cursor.execute(query, params)
        conn.commit()
        return True
    except Error as e:
        print(f"Transaction error: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
