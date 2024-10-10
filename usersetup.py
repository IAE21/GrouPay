from mysql.connector import connect


with connect(
        host='localhost',
        user='root',
        passwd='mysql123',
        database='groupay',
) as conn:
    db_admin = """CREATE USER 'admin'@'localhost' IDENTIFIED BY 'admin123';
                    GRANT INSERT, UPDATE, DELETE, ALTER, SELECT ON *.* TO 'admin'@'localhost';"""
    with conn.cursor() as cur:
        cur.execute(db_admin)