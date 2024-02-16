import subprocess
import cv2
import sqlite3
import os
import wmi as wmi
from flask import Flask, render_template, request, redirect, Response, jsonify, send_file, url_for

app = Flask(__name__)


# Database

def create_database_and_tables():
    # Connect to SQLite database (creates it if not exists)
    conn = sqlite3.connect('config.db')

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Check if users table exists
    cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='users' ''')
    users_table_exists = cursor.fetchone()

    # Check if cameras table exists
    cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='cameras' ''')
    cameras_table_exists = cursor.fetchone()

    # Create users table if not exists
    if not users_table_exists:
        cursor.execute('''CREATE TABLE users (
                            id INTEGER PRIMARY KEY,
                            username TEXT,
                            password TEXT,
                            uuid INTEGER DEFAULT 0,
                            initial_state INTEGER DEFAULT 0
                        )''')

    # Create cameras table if not exists
    if not cameras_table_exists:
        cursor.execute('''CREATE TABLE cameras (
                            id INTEGER PRIMARY KEY,
                            ip1 TEXT,
                            ip2 TEXT,
                            ip3 TEXT,
                            ip4 TEXT,
                            plcip TEXT,
                            plcport INTEGER
                        )''')

    # Commit changes and close connection
    conn.commit()
    conn.close()


def get_system_id():
    try:
        # Connect to Windows Management Instrumentation (WMI)
        c = wmi.WMI()
        # System UUID (Universally Unique Identifier)
        for system in c.Win32_ComputerSystemProduct():
            system_info = system.UUID

    except Exception as e:
        print(f"Error: {e}")
        system_info = "0"

    return system_info


def update_uuid(username, new_uuid):
    # Connect to SQLite database
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()

    # Update UUID for the given username
    cursor.execute('''UPDATE users SET uuid = ? WHERE username = ?''', (new_uuid, username))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"UUID for user '{username}' updated successfully.")


def update_initial_state(username, new_state):
    # Connect to SQLite database
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()

    # Update initial state for the given username
    cursor.execute('''UPDATE users SET initial_state = ? WHERE username = ?''', (new_state, username))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"Initial state for user '{username}' updated successfully.")


def create_new_user(username, password):
    # Connect to SQLite database
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()

    # Insert new user into the users table
    cursor.execute('''INSERT INTO users (username, password)
                      VALUES (?, ?)''', (username, password))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"New user '{username}' created successfully.")

def get_db_connection():
    conn = sqlite3.connect('config.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_post(user,password_1):
    username = user
    password = password_1

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the username exists in the database
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()

    # If user exists, check password
    if user:
        if user['password'] == password:
            # Passwords match, redirect to the next page
            return redirect(url_for('next_page'))
        else:
            return 'Invalid password'
    else:
        print("Something went wrong while login!")

def is_pingable(ip_address):
    """
    Check if an IP address is pingable or not.

    Args:
    - ip_address: A string representing the IP address to be checked.

    Returns:
    - True if the IP address is pingable, False otherwise.
    """
    # Construct the ping command
    ping_command = ["ping", "-c", "1", ip_address]

    # Execute the ping command
    try:
        subprocess.check_output(ping_command)
        return True
    except subprocess.CalledProcessError:
        return False


def retrieve_users_data():
    # Connect to SQLite database
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()

    # Retrieve data from the users table
    cursor.execute('''SELECT * FROM users''')
    users_data = cursor.fetchall()

    # Close connection
    conn.close()

    return users_data

def store_camera_ips(ip1,ip2,ip3,ip4, plcip, plcport):
    # Connect to SQLite database
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()

    # Insert IP addresses into the cameras table
    cursor.execute('''INSERT INTO cameras (ip1, ip2, ip3, ip4, plcip, plcport)
                      VALUES (?, ?, ?, ?, ?, ?)''', (ip1,ip2,ip3,ip4, plcip, plcport))

    # Commit changes and close connection
    conn.commit()
    conn.close()

def check_uuid_and_initial_state(uuid):
    # Connect to SQLite database
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()

    # Check if UUID exists in users table
    cursor.execute('''SELECT uuid, initial_state FROM users WHERE uuid = ?''', (uuid,))
    user_data = cursor.fetchone()

    # Close connection
    conn.close()

    if user_data is None:
        # If UUID not found, add it to the table with initial_state as 0
        add_uuid_to_users(uuid)
        return "Load"
        #return render_template("load.html")  # Redirect to load.html
    else:
        _, initial_state = user_data
        if initial_state == 1:
            return "Live"
            # return render_template("live_feed.html")  # Redirect to live_feed.html
        else:
            return "Load"  # Redirect to load.html

def add_uuid_to_users(uuid):
    # Connect to SQLite database
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()

    # Insert UUID into users table with initial_state as 0
    cursor.execute('''INSERT INTO users (uuid, initial_state) VALUES (?, 0)''', (uuid,))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"UUID '{uuid}' added to users table with initial state 0.")


# --------------------------------------------------------------------------------------------

# creating database
create_database_and_tables()

camera = cv2.VideoCapture(0)


def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Convert the frame to JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def homepage():
    return render_template("login.html")


@app.route('/load', methods=['POST'])
def load():
    username = request.form.get('username')
    password = request.form.get('password')
    # login
    login_post(username,password)

    return render_template("load.html")



@app.route('/next_page')
def next_page():
    current_uuid = get_system_id()
    val= check_uuid_and_initial_state(current_uuid)
    if val == "Load":
        return redirect("/load")
    elif val == "Live":
        return render_template("live_feed.html")
    


@app.route('/signup_page')
def signup_page():
    return render_template("signup.html")


@app.route('/signup', methods=['POST'])
def signup():
    username_2 = request.form.get('username')
    password_2 = request.form.get('password')
    create_new_user(username_2, password_2)
    return render_template("login.html")


@app.route('/ip_setup')
def validate():
    return render_template("home.html")


@app.route("/testing", methods=['POST'])
def testing():
    data = request.form.get('data')
    # camera_ip = 'your_camera_ip'
    # camera_url = 'rtsp://' + camera_ip + '/stream'
    camera_url = int(data)
    cap = cv2.VideoCapture(camera_url)

    while True:
        ret, frame = cap.read()

        if ret:
            with open("static/js/db.txt", 'w') as file:
                file.write('1\n')
                break
        else:
            with open("static/js/db.txt", 'w') as file:
                file.write('0\n')
                break

    with open("static/js/db.txt", 'r') as file:
        content = file.read().strip()

    return content


def redirect_template():
    return render_template('live_feed.html')


@app.route("/live_feed", methods=['POST', 'GET'])
def live_feed():
    data = request.get_json()
    addresses = data.get('addresses')
    ip1 = addresses[0]
    ip2 = addresses[1]
    ip3 = addresses[2]
    ip4 = addresses[3]
    plcip = "172.17"
    plcport = 5000
    store_camera_ips(ip1, ip2, ip3, ip4, plcip, plcport)
    print("Ip stored")
    redirect_template()
    return jsonify({'success': True})


@app.route('/live')
def live():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')





if __name__ == "__main__":
    app.run(debug=True)
