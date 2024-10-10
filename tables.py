from mysql.connector import connect


conn = connect(
        host='localhost',
        user='root',
        passwd='mysql123',
        database='groupay',
        auth_plugin='mysql_native_password'
)
try:
    cur = conn.cursor()
    db_create_groups = """CREATE TABLE IF NOT EXISTS BILLGROUPS(
                            Group_num INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                            Amount INT NOT NULL
                            )"""
    db_create_users = """CREATE TABLE IF NOT EXISTS USERS( 
                            Name VARCHAR(255) NOT NULL,
                            Group_number INT,
                            user_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                            username VARCHAR(50) NOT NULL,
                            password VARCHAR(255) NOT NULL,
                            FOREIGN KEY (Group_number) REFERENCES BILLGROUPS(Group_num)
                            )"""
    cur.execute(db_create_groups)
    cur.execute(db_create_users)
    conn.commit()

finally:
    cur.close()
    conn.close()
