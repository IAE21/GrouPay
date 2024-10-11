from mysql.connector import connect, Error

try:
    with connect(
        host='localhost',
        user='root',
    ) as conn:
        db_create = "CREATE DATABASE IF NOT EXISTS Groupay"
        with conn.cursor() as cur:
            cur.execute(db_create)
            
    with connect(
        host='localhost',
        user='root',
        database='Groupay'
    ) as conn:
        db_create_users = """CREATE TABLE IF NOT EXISTS USERS( 
                            user_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                            fname VARCHAR(100) NOT NULL,
                            lname VARCHAR(100) NOT NULL,
                            company VARCHAR(150),
                            username VARCHAR(50) NOT NULL,
                            password VARCHAR(255) NOT NULL,
                            corporate INT NOT NULL,
                            group_num INT,
                            FOREIGN KEY (group_num) REFERENCES BILL_GROUPS(group_num),
                            UNIQUE KEY uname (username)
                            )"""
        db_create_groups = """CREATE TABLE IF NOT EXISTS BILL_GROUPS(
                            group_num INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                            amount INT NOT NULL,
                            member_ids VARCHAR(500)
                            )"""
        with conn.cursor() as cur:
            cur.execute(db_create_groups)
            cur.execute(db_create_users)
        conn.commit()
except Error as e:
    print(e)
    