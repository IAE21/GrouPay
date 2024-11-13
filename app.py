from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from mysql.connector import Error
import setup

app = Flask(__name__)
app.secret_key = 'cmills'

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "mysql123"
app.config["MYSQL_DB"] = "groupay"


mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pword = request.form['password']
        
        try:
            cur = mysql.connection.cursor()
            valid = cur.execute("SELECT 1 FROM USERS WHERE username=%s AND password=%s", (uname, pword))
            if valid != 0:
                return render_template('dashboard.html')
            flash('Incorrect username or password.', category='error')
        except Error as e:
            print(e)
            return render_template('login.html')
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        uname = request.form['username']
        pword = request.form['password']
        corp = request.form['corporate']

        if corp == '0':
            corp = 0
        else:
            corp = 1
            
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT IGNORE INTO USERS(fname, lname, username, password, corporate) VALUES(%s, %s, %s, %s, %s)", (fname, lname, uname, pword, corp))
            mysql.connection.commit()
            return render_template('login.html')
        except Error as e:
            print(e)
            return render_template('register.html')
                            
    return render_template('register.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
