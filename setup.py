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
                            manager_id INT NOT NULL,
                            group_name VARCHAR(100) NOT NULL,
                            company VARCHAR(150),
                            amount DEC(10,2) NOT NULL,
                            FOREIGN KEY (manager_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE
                            )"""
        db_create_pays = """CREATE TABLE IF NOT EXISTS PAYS_FOR(
                            user_id INT NOT NULL,
                            group_num INT NOT NULL,
                            percent DEC(4,2) NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                            FOREIGN KEY (group_num) REFERENCES BILL_GROUPS(group_num) ON DELETE CASCADE ON UPDATE CASCADE,
                            PRIMARY KEY (user_id, group_num)
                            )"""
        db_create_friend_requests = """CREATE TABLE IF NOT EXISTS FRIEND_REQUESTS(
                                        requester_id INT NOT NULL,
                                        requestee_id INT NOT NULL,
                                        status VARCHAR(20) NOT NULL DEFAULT 'pending',
                                        request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        PRIMARY KEY (requester_id, requestee_id),
                                        FOREIGN KEY (requester_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                                        FOREIGN KEY (requestee_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE
                                        )"""
        db_create_friends = """CREATE TABLE IF NOT EXISTS FRIENDS(
                                user_id INT NOT NULL,
                                friend_id INT NOT NULL,
                                friendship_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                PRIMARY KEY (user_id, friend_id),
                                FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                                FOREIGN KEY (friend_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE
                                )"""
        db_create_group_invites = """CREATE TABLE IF NOT EXISTS GROUP_INVITES(
                                    group_num INT NOT NULL,
                                    sender_id INT NOT NULL,
                                    receiver_id INT NOT NULL,
                                    status VARCHAR(20) NOT NULL DEFAULT 'pending',
                                    invite_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    PRIMARY KEY (group_num, receiver_id),
                                    FOREIGN KEY (group_num) REFERENCES BILL_GROUPS(group_num) ON DELETE CASCADE ON UPDATE CASCADE,
                                    FOREIGN KEY (sender_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                                    FOREIGN KEY (receiver_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE
                                    )"""
        
        db_admin = """CREATE USER IF NOT EXISTS 'admin'@'localhost' IDENTIFIED BY 'admin123';"""
        db_grant = "GRANT INSERT, UPDATE, DELETE, ALTER, SELECT ON *.* TO 'admin'@'localhost';"
        with conn.cursor() as cur:
            cur.execute(db_create_users)
            cur.execute(db_create_groups)
            cur.execute(db_create_pays)
            cur.execute(db_admin)
            cur.execute(db_grant)
            cur.execute(db_create_friend_requests)
            cur.execute(db_create_friends)
            cur.execute(db_create_group_invites)
        conn.commit()
except Error as e:
    print(e)
