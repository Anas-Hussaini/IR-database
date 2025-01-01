import os
import psycopg2
from config import dotenv_path, db_config
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv(
    dotenv_path=dotenv_path,
    override=True,
)

DB_PASSWORD = os.environ["DB_PASSWORD"]


# Function to Connect to POSTGRE Database
def connect_to_db(db_name="postgres"):
    """Establish a connection to the database."""
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_config["user"],
            password=DB_PASSWORD,
            host=db_config["host"],
            port=db_config["port"],
        )
        return conn
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")
    

# Function to execute POSTGRE SQL Query in a Database
def execute_query(conn, query, params=None, fetch=False):
    """Execute a database query."""
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
            return result
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Database query error: {e}")
    finally:
        cursor.close()