from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from flask_mysqldb import MySQL
from mysql.connector import Error
from functools import wraps
import setup

app = Flask(__name__)
app.secret_key = 'cmills'

login_manager = LoginManager()
login_manager.init_app(app)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "mysql123"
app.config["MYSQL_DB"] = "groupay"

mysql = MySQL(app)

@login_manager.user_loader
def load_user(uid):
    current_user = auth.get_user(uid)
    return current_user

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
                cur.execute("SELECT * FROM USERS WHERE username=%s AND password=%s", (uname, pword))
                results = cur.fetchall()
                session['firstname'] = results[0][1]
                session['lastname'] = results[0][2]
                session['company'] = results[0][3]
                session['username'] = results[0][4]
                session['role'] = results[0][6]
                return render_template('dashboard.html', role=session['role'], fname=session['firstname'])
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
    return render_template('dashboard.html', role=session['role'], fname=session['firstname'])

if __name__ == '__main__':
    app.run(debug=True)
