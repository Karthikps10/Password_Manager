from flask import Flask, render_template, jsonify, request, session, redirect, flash,url_for
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sqlite3
import random
import string
import time

app = Flask(__name__)
app.secret_key = 'mycode'

HOST = "smtp.gmail.com"
PORT = 587
FROM_EMAIL = "awsiamuserpwd@gmail.com"
PASSWORD = "wfoo uyyp zzmc ekgt"

#Creating a User database.

def init_db():
    with sqlite3.connect('Users.db') as connect:
        cursor = connect.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS USERS (
                           Email TEXT PRIMARY KEY,
                           Name TEXT,
                           Password TEXT
                        )""")
        connect.commit()

init_db()

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('reg.html')

@app.route('/OTP')
def otp():

    if session.get('otp_verified'):  
        return redirect(url_for('index'))  
    
    email = session.get('email')
    if not email:
        return redirect(url_for('index'))
    return render_template('OTP.html')

@app.route('/forget')
def forget():
    return render_template('forget.html')

@app.route('/generate')
def generate():
    email = session.get('email')
    if not email:
        return redirect(url_for('index'))
    return render_template('generate.html')

@app.route('/update', methods=['POST'])
def confirmEmail():
    data = request.get_json()
    email = data.get('email')
    message = "Temporary password: "
    if not email:
        return jsonify({'message': 'Email is required'}), 400
    with sqlite3.connect('Users.db') as connect:
        cursor = connect.cursor()
        cursor.execute("SELECT Email FROM USERS WHERE Email = ?", (email,))
        result = cursor.fetchone()
        if result :
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            session['email'] = email
            send_otp(email, password, message)
            print(password)
            with sqlite3.connect('Users.db') as connect:
                cursor = connect.cursor()
                cursor.execute("UPDATE USERS SET Password = ? WHERE Email = ?", (password, email))
                connect.commit()
            return jsonify({'message': 'Password shared to email.'}), 200
        else:
            return jsonify({'message': 'Invalid. Please register'}), 401

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    with sqlite3.connect('Users.db') as connect:
        cursor = connect.cursor()
        cursor.execute("SELECT Password FROM USERS WHERE Email = ?", (email,))
        result = cursor.fetchone()

        if result and result[0] == password:
            otp = ''.join(random.choices(string.digits, k=6))
            session['otp'] = otp
            session['email'] = email
            session['otp_time'] = time.time() 
            send_otp(email, otp, message= "Your OTP")
            print(otp)
            return jsonify({'message': 'OTP sent successfully'}), 200           
        else:
            return jsonify({'message': 'Invalid email or password'}), 401

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    if not email or not name or not password:
        return jsonify({'message': 'All fields are required'}), 400
    
    if len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters long'}), 400

    with sqlite3.connect('Users.db') as connect:
        cursor = connect.cursor()
        try:
            cursor.execute("INSERT INTO USERS (Email, Name, Password) VALUES (?, ?, ?)", (email, name, password))
            connect.commit()
            user_db_name = f'{email.replace("@", "_").replace(".", "_")}.db'
            if not os.path.exists(user_db_name):
                with sqlite3.connect(user_db_name) as user_db:
                    user_db.execute('''
                        CREATE TABLE IF NOT EXISTS user_data (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            site TEXT NOT NULL,
                            username TEXT NOT NULL,
                            password TEXT NOT NULL,
                            link TEXT NOT NULL,
                            notes TEXT NOT NULL   
                        )
                    ''')

            return jsonify({'message': 'Registration successful', 'success': True}), 200
        except sqlite3.IntegrityError:
            return jsonify({'message': 'Email already registered', 'success': False}), 400

def send_otp(email, otp, message):
    MESSAGE = f"""Subject: EMAIL VERIFICATION

    {message}: {otp}"""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Your OTP"
    msg['From'] = FROM_EMAIL
    msg['To'] = email
    msg.attach(MIMEText(MESSAGE, 'plain'))
    try:
        with smtplib.SMTP(HOST, PORT) as smtp:
            smtp.starttls()
            smtp.login(FROM_EMAIL, PASSWORD)
            smtp.sendmail(FROM_EMAIL, email, msg.as_string())
    except Exception as e:
        print(f"Failed to send OTP: {str(e)}")

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    # email = data.get('email')
    otp = data.get('otp')

    if not otp:
        return jsonify({'message': 'OTP is required'}), 400

    current_time = time.time()
    otp_time = session.get('otp_time')

    if otp == session.get('otp'):
        if otp_time and (current_time - otp_time <= 180):  
            print(otp, session.get('otp'))
            session['otp_verified'] = True
            main()  
            return jsonify({'message': 'OTP verified successfully'}), 200
        else:
            print(otp, session.get('otp'))

            return jsonify({'message': 'OTP has expired. Log In again'}), 403
    else:
        print(otp, session.get('otp'))
        return jsonify({'message': 'Invalid OTP'}), 400

@app.route('/reset')
def reset():
    return render_template('reset.html')

@app.route('/reset', methods=['POST'])
def reset_pass():
    data = request.get_json()
    email = data.get('email')
    new_password = data.get('new_password')
    password = data.get('password')

    if not email or not new_password or not password:
        return jsonify({'message': 'All fields are required'}), 400

    with sqlite3.connect('Users.db') as connect:
        cursor = connect.cursor()
        cursor.execute("SELECT Password FROM USERS WHERE Email = ?", (email,))
        result = cursor.fetchone()

        if result and result[0] == password:
            with sqlite3.connect('Users.db') as connect:
                cursor = connect.cursor()
                cursor.execute("UPDATE USERS SET Password = ? WHERE Email = ?", (new_password, email))
                connect.commit()
            return jsonify({'message': 'Password updated'}), 200
        else:
            return jsonify({'message': 'Invalid Email or Password'}), 401

@app.route('/main1')
def main():
    email = session.get('email')
    if not email:
        return redirect(url_for('index'))
    
    user_db_name = f'{email.replace("@", "_").replace(".", "_")}.db'
    print(f'User DB Name: {user_db_name}')
    print(f'Attempting to connect to: {user_db_name}')
    if not os.path.exists(user_db_name):
        return render_template('error.html', message='User database does not exist'), 404

    try:
        with sqlite3.connect(user_db_name) as user_db:
            cursor = user_db.cursor()
            cursor.execute('SELECT site, username, password, link, notes FROM user_data')
            entries = cursor.fetchall()
            print(f'Attempting to connect to2: {user_db_name}')
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        print(f'Attempting to connect to3: {user_db_name}')

    print(f'Entries to render: {entries}')
    
    return render_template('main.html', entries=entries)


@app.route('/add', methods=['GET', 'POST'])
def add():
    # Check if the user is logged in
    email = session.get('email')
    print(email)
    if not email:
        return redirect(url_for('index')) 
    
    if request.method == 'POST':

        site = request.form.get('site')
        username = request.form.get('username')
        password = request.form.get('password')
        link = request.form.get('link')
        notes = request.form.get('notes')
        user_db_name = f'{email.replace("@", "_").replace(".", "_")}.db'
        if not os.path.exists(user_db_name):
            flash('User database does not exist.', 'error')
            return redirect(url_for('index')) 
        
        try:
            with sqlite3.connect(user_db_name) as user_db:
                user_db.execute('INSERT INTO user_data (site, username, password, link, notes) VALUES (?, ?, ?, ?, ?)',
                                (site, username, password, link, notes))
                user_db.commit()  
            print('susces')
            flash('Entry added successfully!', 'success')
            return redirect(url_for('main'))  
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            flash('Database error occurred. Please try again.', 'error')
            return redirect(url_for('main')) 
    return render_template('add.html')

@app.route('/edit_entry', methods=['POST'])
def edit_entry():
    email = session.get('email')
    if not email:
        return redirect(url_for('index'))

    data = request.json
    old_site = data.get('oldsite')
    new_site = data.get('newsite')
    username = data.get('username')
    password = data.get('password')
    link = data.get('link')
    notes = data.get('notes')

    user_db_name = f'{email.replace("@", "_").replace(".", "_")}.db'

    try:
        with sqlite3.connect(user_db_name) as user_db:
            cursor = user_db.cursor()
            cursor.execute('''
                UPDATE user_data
                SET site = ?, username = ?, password = ?, link = ?, notes = ?
                WHERE site = ?
            ''', (new_site, username, password, link, notes, old_site))
            user_db.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({'status': 'error', 'message': 'Database error occurred'}), 500

    return jsonify({'status': 'success'})

@app.route('/delete_entry', methods=['POST'])
def delete_entry():
    email = session.get('email')
    if not email:
        return redirect(url_for('index'))

    data = request.json
    site = data.get('site')

    user_db_name = f'{email.replace("@", "_").replace(".", "_")}.db'

    try:
        with sqlite3.connect(user_db_name) as user_db:
            cursor = user_db.cursor()
            cursor.execute('DELETE FROM user_data WHERE site = ?', (site,))
            user_db.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({'status': 'error', 'message': 'Database error occurred'}), 500

    return jsonify({'status': 'success'})

@app.route('/copy_to_clipboard', methods=['POST'])
def copy_to_clipboard():
    data = request.json
    text = data.get('text')
    return jsonify({'status': 'success', 'message': 'Text to be copied'})

if __name__ == '__main__':
    app.run( host ='0.0.0.0', port = 8000)
