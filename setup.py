from mysql.connector import connect


with connect(
        host='localhost',
        user='root',
        passwd='mysql123',
) as conn:
    db_create = "CREATE DATABASE IF NOT EXISTS groupay"
    with conn.cursor() as cur:
        cur.execute(db_create)