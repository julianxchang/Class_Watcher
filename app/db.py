import os
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

connection_pool = pool.SimpleConnectionPool(
    1,
    10,
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

def get_db_conn():
    """Get a connection from the pool"""
    conn = connection_pool.getconn()
    return conn

def release_db_conn(conn):
    """Return a connection back to the pool"""
    connection_pool.putconn(conn)