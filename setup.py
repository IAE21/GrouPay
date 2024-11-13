from mysql.connector import connect, Error

try:
    with connect(
        host='localhost',
        user='root',
        password='mysql123'
    ) as conn:
        db_create = "CREATE DATABASE IF NOT EXISTS groupay"
        with conn.cursor() as cur:
            cur.execute(db_create)
            
    with connect(
        host='localhost',
        user='root',
        password='mysql123',
        database='groupay'
    ) as conn:
        db_create_users = """CREATE TABLE IF NOT EXISTS USERS( 
                            user_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                            fname VARCHAR(100) NOT NULL,
                            lname VARCHAR(100) NOT NULL,
                            company VARCHAR(150),
                            username VARCHAR(50) NOT NULL,
                            password VARCHAR(255) NOT NULL,
                            corporate INT NOT NULL,
                            UNIQUE KEY uname (username)
                            )"""
        db_create_groups = """CREATE TABLE IF NOT EXISTS BILL_GROUPS(
                            group_num INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                            group_name VARCHAR(100),
                            company VARCHAR(150),
                            amount DEC(10,2) NOT NULL,
                            )"""
        db_create_pays = """CREATE TABLE IF NOT EXISTS PAYS_FOR(
                            user_id INT NOT NULL,
                            group_num INT NOT NULL,
                            percent DEC(4,2) NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                            FOREIGN KEY (group_num) REFERENCES BILL_GROUPS(group_num) ON DELETE CASCADE ON UPDATE CASCADE,
                            PRIMARY KEY (user_id, group_num)
                            )"""
        db_admin = """CREATE USER IF NOT EXISTS 'admin'@'localhost' IDENTIFIED BY 'admin123';"""
        db_grant = "GRANT INSERT, UPDATE, DELETE, ALTER, SELECT ON *.* TO 'admin'@'localhost';"
        with conn.cursor() as cur:
            cur.execute(db_create_groups)
            cur.execute(db_create_users)
            cur.execute(db_create_pays)
            cur.execute(db_admin)
            cur.execute(db_grant)
        conn.commit()
except Error as e:
    print(e)
