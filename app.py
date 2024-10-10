from flask import Flask, render_template, request, redirect, url_for
from mysql.connector import connect
from flask_mysqldb import MySQL
app = Flask(__name__)

app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "mysql123"
app.config["MYSQL_DB"] = "groupay"

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        conn = connect(
            host='localhost',
            user='root',
            passwd='mysql123',
            database='groupay',
            )
        cur = conn.cursor()
        try:
            cur.execute("""
                        INSERT INTO USERS (username, password, name)
                        VALUES (%s, %s, %s)
                        """,
                        (username, password, name))
            conn.commit()
            return redirect(url_for('login'))
        finally:
            cur.close()
            conn.close()
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
