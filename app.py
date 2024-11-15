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

def fetch_glist():
    u_id = session['userID']
    try:
        cur = mysql.connection.cursor()
        if session['role'] == 1:
            cur.execute("SELECT fname, lname, group_name, amount, group_num FROM USERS, BILL_GROUPS WHERE USERS.user_id = BILL_GROUPS.manager_id AND manager_id=%s", (u_id,))
        else:
            cur.execute("SELECT fname, lname, group_name, amount, BILL_GROUPS.group_num FROM USERS, BILL_GROUPS, PAYS_FOR WHERE USERS.user_id = BILL_GROUPS.manager_id AND PAYS_FOR.group_num = BILL_GROUPS.group_num AND PAYS_FOR.user_id=%s", (u_id,))
        glist = cur.fetchall()
    except Error as e:
        print(e)
    return glist
    
    
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
                session['userID'] = results[0][0]
                session['firstname'] = results[0][1]
                session['lastname'] = results[0][2]
                session['company'] = results[0][3]
                session['username'] = results[0][4]
                session['role'] = results[0][6]
                glist = fetch_glist()
                return render_template('dashboard.html', role=session['role'], fname=session['firstname'], glist=glist)
            flash('Incorrect username or password.', category='error')
        except Error as e:
            print(e)
            return render_template('login.html')
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        comp = request.form['company']
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
            cur.execute("INSERT IGNORE INTO USERS(fname, lname, company, username, password, corporate) VALUES(%s, %s, %s, %s, %s, %s)", (fname, lname, comp, uname, pword, corp))
            mysql.connection.commit()
            return render_template('login.html')
        except Error as e:
            print(e)
            return render_template('register.html')
                            
    return render_template('register.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    glist = fetch_glist()
    return render_template('dashboard.html', role=session['role'], fname=session['firstname'], glist=glist)

@app.route('/createGroup', methods=['GET', 'POST'])
def createGroup():
    if request.method == 'POST':
        mgrID = session['userID']
        gname = request.form['groupname']
        comp = session['company']
        amt = request.form['amount']
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT IGNORE INTO BILL_GROUPS(manager_id, group_name, company, amount) VALUES(%s, %s, %s, %s)", (mgrID, gname, comp, amt))
            mysql.connection.commit()
            glist = fetch_glist()
            return render_template('dashboard.html', role=session['role'], fname=session['firstname'], glist=glist)
        except Error as e:
            print(e)
            return render_template('createGroup.html', role=session['role'])
    
    return render_template('createGroup.html', role=session['role'])

@app.route('/searchGroups', methods=['GET', 'POST'])
def searchGroups():
    if request.method == 'POST':
        gname = request.form['groupname']
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT fname, lname, group_name, amount, group_num FROM USERS, BILL_GROUPS WHERE USERS.user_id = BILL_GROUPS.manager_id AND group_name=%s", (gname,))
            glist = cur.fetchall()
            return render_template('searchGroups.html', role=session['role'], fname=session['firstname'], glist=glist)
        except Error as e:
            print(e)
            return render_template('searchGroups.html', role=session['role'], fname=session['firstname'], glist=glist)
    
    return render_template('searchGroups.html', role=session['role'])

@app.route('/joinGroup', methods=['POST'])
def joinGroup():
    if request.method == 'POST':
        uid = session['userID']
        gnum = request.form['groupnum']
        count = 0
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT COUNT(*) FROM (SELECT * FROM PAYS_FOR WHERE group_num=%s) AS MEMS", (gnum,))
            results = cur.fetchall()
            count = results[0][0]
        except Error as e:
            print(e)
            
        perc = 100/(count + 1)
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT IGNORE INTO PAYS_FOR(user_id, group_num, percent) VALUES(%s, %s, %s)", (uid, gnum, perc))
            mysql.connection.commit()
            glist = fetch_glist()
            return render_template('dashboard.html', role=session['role'], fname=session['firstname'], glist=glist)
        except Error as e:
            print(e)
            return render_template('searchGroups.html', role=session['role'])
        
@app.route('/manageGroup', methods=['GET', 'POST'])
def manageGroup():
    if request.method == 'POST':
        gnum = request.form['groupnum']

        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT fname, lname, group_name, amount FROM USERS, BILL_GROUPS WHERE USERS.user_id = BILL_GROUPS.manager_id AND group_num=%s", (gnum,))
            billgroup = cur.fetchall()
            mgr_name = billgroup[0][0] + ' ' + billgroup[0][1]
            gname = billgroup[0][2]
            amount = billgroup[0][3]
            cur.execute("SELECT fname, lname, username, percent FROM USERS, PAYS_FOR WHERE USERS.user_id = PAYS_FOR.user_id AND group_num=%s", (gnum,))
            mlist = cur.fetchall()
            return render_template('manageGroup.html', role=session['role'], gname=gname, mgr=mgr_name, amount=amount, mlist=mlist)
        except Error as e:
            print(e)
            glist = fetch_glist()
            return render_template('dashboard.html', role=session['role'], fname=session['firstname'], glist=glist)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('firstname', None)
    session.pop('lastname', None)
    session.pop('company', None)
    session.pop('username', None)
    session.pop('role', None)
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
