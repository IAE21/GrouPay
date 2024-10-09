from mysql.connector import connect


conn = connect(
    host='localhost',
    user='root',
    passwd='mysql123',
    auth_plugin='mysql_native_password'
)
try:
    db_create = "CREATE DATABASE IF NOT EXISTS groupay"
    cur = conn.cursor()
    cur.execute(db_create)
finally:
    cur.close()
    conn.close()
