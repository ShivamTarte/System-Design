from mysql.connector import pooling
import os
from dotenv import load_dotenv
load_dotenv()

table="user_info"

def get_db_pool():#connection pool
    return pooling.MySQLConnectionPool(
        pool_name="my_pool",
        pool_size=5,
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="shard1"
    )


def fetch_data(user: str,connection=get_db_pool):
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {table} WHERE username = %s", (user,))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result