from mysql.connector import connect


with connect(
        host='localhost',
        user='root',
        passwd='mysql123',
        database='groupay',
) as conn:
    db_create_groups = """CREATE TABLE IF NOT EXISTS BILLGROUPS(
                            Group_num INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                            Amount INT NOT NULL
                            )"""
    db_create_users = """CREATE TABLE IF NOT EXISTS USERS( 
                            Name VARCHAR(255) NOT NULL,
                            Group_number INT NOT NULL AUTO_INCREMENT,
                            FOREIGN KEY (Group_number) REFERENCES BILLGROUPS(Group_num)
                            )"""
    with conn.cursor() as cur:
        cur.execute(db_create_groups)
        cur.execute(db_create_users)