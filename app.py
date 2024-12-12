from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager
from flask_mysqldb import MySQL
from mysql.connector import Error
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
    
def fetch_invlist():
    u_id = session['userID']
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
                    SELECT GROUP_INVITES.group_num, BILL_GROUPS.group_name, BILL_GROUPS.amount,
                        USERS.fname, USERS.lname, GROUP_INVITES.sender_id
                    FROM GROUP_INVITES
                    JOIN BILL_GROUPS ON GROUP_INVITES.group_num = BILL_GROUPS.group_num
                    JOIN USERS ON GROUP_INVITES.sender_id = USERS.user_id
                    WHERE GROUP_INVITES.receiver_id = %s AND GROUP_INVITES.status = 'pending'
                    """, (u_id,))
        pending_invites = cur.fetchall()
        mgr_names = []
        for inv in pending_invites:
            cur.execute("""SELECT fname, lname FROM USERS JOIN BILL_GROUPS ON manager_id = user_id WHERE group_num = %s""", (inv[0],))
            mgrs = cur.fetchall()
            mgr_names.append(mgrs[0])
    except Error as e:
        print(e)
    return (pending_invites, mgr_names)
        
def check_empty(pending_invlist):
    if len(pending_invlist[0]) > 0 and len(pending_invlist[1]) > 0:
        no_invs = "false"
    else:
        no_invs = "true"
    return no_invs
    
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
                pending_invlist = fetch_invlist()
                no_invs = check_empty(pending_invlist)
                return render_template('dashboard.html', user=session, glist=glist, pending_invites=zip(pending_invlist[0], pending_invlist[1]), no_invs=no_invs)
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
    pending_invlist = fetch_invlist()
    no_invs = check_empty(pending_invlist)
    return render_template('dashboard.html', user=session, glist=glist, pending_invites=zip(pending_invlist[0], pending_invlist[1]), no_invs=no_invs)

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
            pending_invlist = fetch_invlist()
            no_invs = check_empty(pending_invlist)
            return render_template('dashboard.html', user=session, glist=glist, pending_invites=zip(pending_invlist[0], pending_invlist[1]), no_invs=no_invs)
        except Error as e:
            print(e)
            return render_template('createGroup.html', user=session )
    
    return render_template('createGroup.html', user=session, )

@app.route('/searchGroups', methods=['GET', 'POST'])
def searchGroups():
    if request.method == 'POST':
        gname = request.form['groupname']
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT fname, lname, group_name, amount, group_num FROM USERS, BILL_GROUPS WHERE USERS.user_id = BILL_GROUPS.manager_id AND group_name=%s", (gname,))
            glist = cur.fetchall()
            return render_template('searchGroups.html', user=session, glist=glist)
        except Error as e:
            print(e)
            return render_template('searchGroups.html', user=session, glist=glist)
    
    return render_template('searchGroups.html', user=session)

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
            pending_invlist = fetch_invlist()
            no_invs = check_empty(pending_invlist)
            return render_template('dashboard.html', user=session, glist=glist, pending_invites=zip(pending_invlist[0], pending_invlist[1]), no_invs=no_invs)
        except Error as e:
            print(e)
            return render_template('searchGroups.html', user=session)
        
@app.route('/manageGroup', methods=['GET', 'POST'])
def manageGroup():
    if request.method == 'POST':
        gnum = request.form['groupnum']

        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT fname, lname, group_name, amount, user_id FROM USERS, BILL_GROUPS WHERE USERS.user_id = BILL_GROUPS.manager_id AND group_num=%s", (gnum,))
            billgroup = cur.fetchall()
            mgr_name = billgroup[0][0] + ' ' + billgroup[0][1]
            gname = billgroup[0][2]
            amount = billgroup[0][3]
            mgr_id = billgroup[0][4]
            cur.execute("SELECT fname, lname, username, percent, USERS.user_id FROM USERS, PAYS_FOR WHERE USERS.user_id = PAYS_FOR.user_id AND group_num=%s", (gnum,))
            mlist = cur.fetchall()
            return render_template('manageGroup.html', user=session, gname=gname, gnum=gnum, mgr=mgr_name, mgr_id=mgr_id, amount=amount, mlist=mlist)
        except Error as e:
            print(e)
            glist = fetch_glist()
            pending_invlist = fetch_invlist()
            no_invs = check_empty(pending_invlist)
            return render_template('dashboard.html', user=session, glist=glist, pending_invites=zip(pending_invlist[0], pending_invlist[1]), no_invs=no_invs)

@app.route('/editAmount', methods=['POST'])
def editAmount():
    gnum = request.form['gnum']
    amt = request.form['amt']
    try:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE BILL_GROUPS SET amount = %s WHERE group_num = %s", (amt, gnum))
        mysql.connection.commit()
        cur.execute("SELECT fname, lname, group_name, amount, user_id FROM USERS, BILL_GROUPS WHERE USERS.user_id = BILL_GROUPS.manager_id AND group_num=%s", (gnum,))
        billgroup = cur.fetchall()
        mgr_name = billgroup[0][0] + ' ' + billgroup[0][1]
        gname = billgroup[0][2]
        amount = billgroup[0][3]
        mgr_id = billgroup[0][4]
        cur.execute("SELECT fname, lname, username, percent, USERS.user_id FROM USERS, PAYS_FOR WHERE USERS.user_id = PAYS_FOR.user_id AND group_num=%s", (gnum,))
        mlist = cur.fetchall()
        return render_template('manageGroup.html', user=session, gname=gname, gnum=gnum, mgr=mgr_name, mgr_id=mgr_id, amount=amount, mlist=mlist)
    except Error as e:
        print(e)
        glist = fetch_glist()
        pending_invlist = fetch_invlist()
        no_invs = check_empty(pending_invlist)
        return render_template('dashboard.html', user=session, glist=glist, pending_invites=zip(pending_invlist[0], pending_invlist[1]), no_invs=no_invs)
    
@app.route('/editPercentage', methods=['POST'])
def editPercentage():
    gnum = request.form['gnum']
    editID = request.form['editID']
    perc = request.form['perc']
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT fname, lname, group_name, amount, user_id FROM USERS, BILL_GROUPS WHERE USERS.user_id = BILL_GROUPS.manager_id AND group_num=%s", (gnum,))
        billgroup = cur.fetchall()
        mgr_name = billgroup[0][0] + ' ' + billgroup[0][1]
        gname = billgroup[0][2]
        amount = billgroup[0][3]
        mgr_id = billgroup[0][4]
        cur.execute("UPDATE PAYS_FOR SET percent = %s WHERE user_id = %s AND group_num = %s", (perc, editID, gnum))
        mysql.connection.commit()
        cur.execute("SELECT fname, lname, username, percent, USERS.user_id FROM USERS, PAYS_FOR WHERE USERS.user_id = PAYS_FOR.user_id AND group_num=%s", (gnum,))
        mlist = cur.fetchall()
        return render_template('manageGroup.html', user=session, gname=gname, gnum=gnum, mgr=mgr_name, mgr_id=mgr_id, amount=amount, mlist=mlist)
    except Error as e:
        print(e)
        glist = fetch_glist()
        pending_invlist = fetch_invlist()
        no_invs = check_empty(pending_invlist)
        return render_template('dashboard.html', user=session, glist=glist, pending_invites=zip(pending_invlist[0], pending_invlist[1]), no_invs=no_invs)

@app.route('/removeGroupUser', methods=['POST'])
def removeGroupUser():
    user_id = request.form['user_id']
    gnum = request.form['gnum']
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM PAYS_FOR WHERE user_id = %s AND group_num = %s", (user_id, gnum))
        mysql.connection.commit()
        cur.execute("SELECT fname, lname, group_name, amount, user_id FROM USERS, BILL_GROUPS WHERE USERS.user_id = BILL_GROUPS.manager_id AND group_num=%s", (gnum,))
        billgroup = cur.fetchall()
        mgr_name = billgroup[0][0] + ' ' + billgroup[0][1]
        gname = billgroup[0][2]
        amount = billgroup[0][3]
        mgr_id = billgroup[0][4]
        cur.execute("SELECT fname, lname, username, percent, USERS.user_id FROM USERS, PAYS_FOR WHERE USERS.user_id = PAYS_FOR.user_id AND group_num=%s", (gnum,))
        mlist = cur.fetchall()
        flash('User removed.', category='success')
        return render_template('manageGroup.html', user=session, gname=gname, gnum=gnum, mgr=mgr_name, mgr_id=mgr_id, amount=amount, mlist=mlist)
    except Error as e:
            print(e)
            glist = fetch_glist()
            pending_invlist = fetch_invlist()
            no_invs = check_empty(pending_invlist)
            return render_template('dashboard.html', user=session, glist=glist, pending_invites=zip(pending_invlist[0], pending_invlist[1]), no_invs=no_invs)
    
@app.route('/searchUsers', methods=['GET', 'POST'])
def searchUsers():
    if request.method == 'POST':
        search_username = request.form['username']
        try:
            cur = mysql.connection.cursor()
            cur.execute("""SELECT user_id, fname, lname, username FROM USERS 
                        WHERE username LIKE %s 
                        AND user_id != %s
                        """, ('%' + search_username + '%', session['userID']))
            user_list = cur.fetchall()
            return render_template('searchUsers.html', user=session, user_list=user_list)
        
        except Error as e:
            print(e)
            glist = fetch_glist()
            pending_invlist = fetch_invlist()
            no_invs = check_empty(pending_invlist)
            return render_template('dashboard.html', user=session, glist=glist, pending_invites=zip(pending_invlist[0], pending_invlist[1]), no_invs=no_invs)
    else:
        # GET
        return render_template('searchUsers.html', user=session)

@app.route('/viewUser/<int:user_id>', methods=['GET'])
def viewUser(user_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""SELECT user_id, fname, lname, username 
                    FROM USERS WHERE user_id = %s""", (user_id,))
        user = cur.fetchone()

        if not user:
            flash('User not found.', category='error')
            return redirect(url_for('searchUsers'))
        return render_template('viewUser.html', cur_user=session, found_user=user)
        
    except Error as e:
            print(e)
            glist = fetch_glist()
            pending_invlist = fetch_invlist()
            no_invs = check_empty(pending_invlist)
            return render_template('dashboard.html', user=session, glist=glist, pending_invites=zip(pending_invlist[0], pending_invlist[1]), no_invs=no_invs)

@app.route('/sendFriendRequest', methods=['POST'])
def sendFriendRequest():
    requester_id = session['userID']
    requestee_id = request.form['user_id']

    try:
        cur = mysql.connection.cursor()

        cur.execute("""
                    SELECT * FROM FRIENDS 
                    WHERE (user_id = %s AND friend_id = %s) 
                    OR (user_id = %s AND friend_id = %s)
                    """, (requester_id, requestee_id, requestee_id, requester_id))
        existing_friendship = cur.fetchone()
        if existing_friendship:
            flash('You are already friends with this user.', category='error')
            return redirect(url_for('viewUser', user_id=requestee_id))
        
        cur.execute("""SELECT * FROM FRIEND_REQUESTS 
                    WHERE requester_id = %s 
                    AND requestee_id = %s""", (requester_id, requestee_id))
        existing_request = cur.fetchone()
        if existing_request:
            flash('Friend request already sent.', category='error')

        else:
            cur.execute("""INSERT INTO FRIEND_REQUESTS (requester_id, requestee_id) VALUES (%s, %s)
                        """, (requester_id, requestee_id))
            mysql.connection.commit()
            flash('Friend request sent!', category='success')
        return redirect(url_for('viewUser', user_id=requestee_id))
    
    except Error as e:
            print(e)
            glist = fetch_glist()
            pending_invlist = fetch_invlist()
            no_invs = check_empty(pending_invlist)
            return render_template('dashboard.html', user=session, glist=glist, pending_invites=zip(pending_invlist[0], pending_invlist[1]), no_invs=no_invs)

@app.route('/friends', methods=['GET'])
def friends():
    user_id = session['userID']
    try: 
        cur = mysql.connection.cursor()

        # USERS FRIENDS
        cur.execute("""
                    SELECT USERS.user_id, USERS.fname, USERS.lname, USERS.username FROM FRIENDS
                    JOIN USERS ON FRIENDS.friend_id = USERS.user_id
                    WHERE FRIENDS.user_id = %s
                    """, (user_id,))
        friends_list = cur.fetchall()

        # REQUESTS
        cur.execute("""
                    SELECT USERS.user_id, USERS.fname, USERS.lname, USERS.username FROM FRIEND_REQUESTS
                    JOIN USERS ON FRIEND_REQUESTS.requester_id = USERS.user_id
                    WHERE FRIEND_REQUESTS.requestee_id = %s AND FRIEND_REQUESTS.status = 'pending'
                    """, (user_id,))
        friend_requests = cur.fetchall()

        return render_template('friends.html', friends_list=friends_list, friend_requests=friend_requests, user=session)
    except Error as e:
            print(e)
            glist = fetch_glist()
            pending_invlist = fetch_invlist()
            no_invs = check_empty(pending_invlist)
            return render_template('dashboard.html', user=session, glist=glist, pending_invites=zip(pending_invlist[0], pending_invlist[1]), no_invs=no_invs)
    
@app.route('/acceptFriendRequest', methods=['POST'])
def acceptFriendRequest():
    user_id = session['userID']
    requester_id = request.form['requester_id']
    try:
        cur = mysql.connection.cursor()

        cur.execute("""
                    DELETE FROM FRIEND_REQUESTS 
                    WHERE requester_id = %s AND requestee_id = %s
                    """, (requester_id, user_id))
        
        cur.execute("""
                    UPDATE FRIEND_REQUESTS SET status = 'accepted' 
                    WHERE requester_id = %s AND requestee_id = %s
                    """, (requester_id, user_id))
        
        cur.execute("""
                    INSERT IGNORE INTO FRIENDS (user_id, friend_id) VALUES (%s, %s), (%s, %s)
                    """, (user_id, requester_id, requester_id, user_id))
        mysql.connection.commit()

        flash('Friend request accepted!', category='success')
        return redirect(url_for('friends'))
    
    except Error as e:
            print(e)
            glist = fetch_glist()
            pending_invlist = fetch_invlist()
            no_invs = check_empty(pending_invlist)
            return render_template('dashboard.html', user=session, glist=glist, pending_invites=zip(pending_invlist[0], pending_invlist[1]), no_invs=no_invs)
    
@app.route('/declineFriendRequest', methods=['POST'])
def declineFriendRequest():
    user_id = session['userID']
    requester_id = request.form['requester_id']
    try:
        cur = mysql.connection.cursor()

        cur.execute("""
                    DELETE FROM FRIEND_REQUESTS 
                    WHERE requester_id = %s AND requestee_id = %s
                    """, (requester_id, user_id))
        mysql.connection.commit()

        flash('Friend request declined.', category='success')
        return redirect(url_for('friends'))
    
    except Error as e:
            print(e)
            glist = fetch_glist()
            pending_invlist = fetch_invlist()
            no_invs = check_empty(pending_invlist)
            return render_template('dashboard.html', user=session, glist=glist, pending_invites=zip(pending_invlist[0], pending_invlist[1]), no_invs=no_invs)

@app.route('/removeFriend', methods=['POST'])
def removeFriend():
    user_id = session['userID']
    friend_id = request.form['friend_id']
    try:
        cur = mysql.connection.cursor()

        cur.execute("""
                    DELETE FROM FRIENDS 
                    WHERE (user_id = %s AND friend_id = %s) 
                    OR (user_id = %s AND friend_id = %s)
                    """, (user_id, friend_id, friend_id, user_id))
        mysql.connection.commit()

        cur.execute("""
                    DELETE FROM FRIEND_REQUESTS 
                    WHERE (requester_id = %s AND requestee_id = %s) 
                    OR (requester_id = %s AND requestee_id = %s)
                    """, (user_id, friend_id, friend_id, user_id))
        mysql.connection.commit()

        flash('Friend removed.', category='success')
        return redirect(url_for('friends'))
    
    except Error as e:
            print(e)
            glist = fetch_glist()
            pending_invlist = fetch_invlist()
            no_invs = check_empty(pending_invlist)
            return render_template('dashboard.html', user=session, glist=glist, pending_invites=zip(pending_invlist[0], pending_invlist[1]), no_invs=no_invs)

@app.route('/inviteToGroup', methods=['POST'])
def inviteToGroup():
    user_id = session['userID']
    friend_id = request.form['friend_id']
    try:
        cur = mysql.connection.cursor()
        
        cur.execute("""
                    SELECT DISTINCT BILL_GROUPS.group_num, BILL_GROUPS.group_name 
                    FROM BILL_GROUPS 
                    LEFT JOIN PAYS_FOR ON BILL_GROUPS.group_num = PAYS_FOR.group_num
                    WHERE PAYS_FOR.user_id = %s OR BILL_GROUPS.manager_id = %s
                    """, (user_id, user_id))
        groups = cur.fetchall()

        if not groups:
            flash('You are not a member of any groups.', category='error')
            return redirect(url_for('friends'))
        return render_template('inviteToGroup.html', user=session, groups=groups, friend_id=friend_id)
    
    except Error as e:
            print(e)
            glist = fetch_glist()
            pending_invlist = fetch_invlist()
            no_invs = check_empty(pending_invlist)
            return render_template('dashboard.html', user=session, glist=glist, pending_invites=zip(pending_invlist[0], pending_invlist[1]), no_invs=no_invs)

@app.route('/sendGroupInvite', methods=['POST'])
def sendGroupInvite():
    sender_id = session['userID']
    receiver_id = request.form['receiver_id']
    group_num = request.form['group_num']
    try:
        cur = mysql.connection.cursor()
        
        cur.execute("""
                    SELECT * FROM PAYS_FOR WHERE user_id = %s 
                    AND group_num = %s
                    """, (receiver_id, group_num))
        is_member = cur.fetchone()
        if is_member:
            flash('User is already a member of this group.', category='error')
            return redirect(url_for('friends'))

        cur.execute("""
                    SELECT * FROM GROUP_INVITES WHERE group_num = %s 
                    AND receiver_id = %s AND status = 'pending'
                    """, (group_num, receiver_id))
        existing_invite = cur.fetchone()

        if existing_invite:
            flash('An invite to this group has already been sent to this user.', category='error')
        else:
            cur.execute("""
                        INSERT IGNORE INTO GROUP_INVITES (group_num, sender_id, receiver_id) VALUES (%s, %s, %s)
                        """, (group_num, sender_id, receiver_id))
            mysql.connection.commit()
            flash('Group invite sent!', category='success')
        return redirect(url_for('friends'))
    
    except Error as e:
            print(e)
            glist = fetch_glist()
            pending_invlist = fetch_invlist()
            no_invs = check_empty(pending_invlist)
            return render_template('dashboard.html', user=session, glist=glist, pending_invites=zip(pending_invlist[0], pending_invlist[1]), no_invs=no_invs)

@app.route('/acceptGroupInvite', methods=['POST'])
def acceptGroupInvite():
    user_id = session['userID']
    group_num = request.form['group_num']

    try:
        cur = mysql.connection.cursor()
        
        cur.execute("""
                    DELETE FROM GROUP_INVITES 
                    WHERE group_num = %s AND receiver_id = %s
                    """, (group_num, user_id))
        
        # CALCUATE NEW PAYS_FOR
        cur.execute("""
                    SELECT COUNT(*) FROM PAYS_FOR WHERE group_num = %s
                    """, (group_num,))
        count = cur.fetchone()[0]
        # Using 100 causes this to break but 99.99 works
        # I think becuase of the way the decimal is stored as DEC(4,2)
        new_percent = 99.99 / (count + 1)

        cur.execute("""
                    UPDATE PAYS_FOR SET percent = %s WHERE group_num = %s
                    """, (new_percent, group_num))
        cur.execute("""
                    INSERT INTO PAYS_FOR (user_id, group_num, percent) VALUES (%s, %s, %s) 
                    """, (user_id, group_num, new_percent))
        
        mysql.connection.commit()
        flash('You have joined the group!', category='success')
        return redirect(url_for('dashboard'))
    
    except Error as e:
            print(e)
            glist = fetch_glist()
            pending_invlist = fetch_invlist()
            no_invs = check_empty(pending_invlist)
            return render_template('dashboard.html', user=session, glist=glist, pending_invites=zip(pending_invlist[0], pending_invlist[1]), no_invs=no_invs)

@app.route('/declineGroupInvite', methods=['POST'])
def declineGroupInvite():

    user_id = session['userID']
    group_num = request.form['group_num']
    try:
        cur = mysql.connection.cursor()
        
        cur.execute("""
                    DELETE FROM GROUP_INVITES
                    WHERE group_num = %s AND receiver_id = %s
                    """, (group_num, user_id))
        mysql.connection.commit()

        flash('You have declined the group invite.', category='success')
        return redirect(url_for('dashboard'))
    except Error as e:
            print(e)
            glist = fetch_glist()
            pending_invlist = fetch_invlist()
            no_invs = check_empty(pending_invlist)
            return render_template('dashboard.html', user=session, glist=glist, pending_invites=zip(pending_invlist[0], pending_invlist[1]), no_invs=no_invs)

@app.route('/profile', methods=['GET','POST'])
def profile():
    return render_template('profile.html', user=session)

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
