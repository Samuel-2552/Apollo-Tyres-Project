import subprocess
import cv2
import sqlite3
import pythoncom
import os
from datetime import datetime
from jinja2 import Template, FileSystemLoader, Environment
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
                            username TEXT UNIQUE,
                            password TEXT,
                            uuid TEXT DEFAULT 0,
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
        # Initialize the COM library
        pythoncom.CoInitialize()

        # Connect to Windows Management Instrumentation (WMI)
        c = wmi.WMI()

        # System UUID (Universally Unique Identifier)
        for system in c.Win32_ComputerSystemProduct():
            system_info = system.UUID
            print(system_info)

    except Exception as e:
        print(f"Error: {e}")
        system_info = "0"

    finally:
        # Uninitialize the COM library
        pythoncom.CoUninitialize()

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


def update_initial_state(uuid, new_state):
    # Connect to SQLite database
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()

    # Update initial state for the given username
    cursor.execute('''UPDATE users SET initial_state = ? WHERE uuid = ?''', (new_state, uuid))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"Initial state for user '{uuid}' updated successfully.")


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


def login_post(user, password_1):
    username = user
    password = password_1

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if the username exists in the database
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user_row = cursor.fetchone()

        if user:
            user_password = user_row['password']
            if user_password == password:
                # Passwords match, redirect to the next page
                print("Password correct")
                return True
            else:
                return False
        else:
            print("User not found in the database")
            return False
    except Exception as e:
        print("Error:", e)
        return False
    finally:
        conn.close()


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


def store_camera_ips(ip1, ip2, ip3, ip4, plcip, plcport):
    # Connect to SQLite database
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()

    # Insert IP addresses into the cameras table
    cursor.execute('''INSERT INTO cameras (ip1, ip2, ip3, ip4, plcip, plcport)
                      VALUES (?, ?, ?, ?, ?, ?)''', (ip1, ip2, ip3, ip4, plcip, plcport))

    # Commit changes and close connection
    conn.commit()
    conn.close()


def check_uuid_and_initial_state(uuid, username):
    # Connect to SQLite database
    print("Checking uuid.........")
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    print(uuid)
    # Check if UUID exists in users table
    cursor.execute('''SELECT uuid, initial_state FROM users WHERE uuid = ?''', (uuid,))
    user_data = cursor.fetchone()

    # Close connection
    conn.close()

    if user_data is None:
        # If UUID not found, add it to the table with initial_state as 0
        add_uuid_to_users(uuid, username)
        return "Load"
        # return render_template("load.html")  # Redirect to load.html
    else:
        _, initial_state = user_data
        if initial_state == 1:
            return "Live"
            # return render_template("live_feed.html")  # Redirect to live_feed.html
        else:
            return "Load"  # Redirect to load.html


def add_uuid_to_users(uuid, username):
    # Connect to SQLite database
    print("added uuid")
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    # Update the row corresponding to the username with the UUID
    cursor.execute('''UPDATE users SET uuid = ?, initial_state = 0 WHERE username = ?''', (uuid, username))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"UUID '{uuid}' added to users table for username '{username}' with initial state 0.")

def create_table():
    conn = sqlite3.connect('config.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS record
                 (camera TEXT, screenshot_location TEXT, timestamp TEXT,No_of_Tyres_Jammed INTEGER(20))''')
    conn.commit()
    conn.close()

def update_record(camera, screenshot_location,no_of_tyres):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect('config.db')
    c = conn.cursor()
    c.execute('''INSERT INTO record (camera, screenshot_location, timestamp, No_of_Tyres_Jammed)
                 VALUES (?, ?, ?, ?)''', (camera, screenshot_location, timestamp, no_of_tyres))
    conn.commit()
    conn.close()

def fetch_records():
    conn = sqlite3.connect('config.db')
    c = conn.cursor()
    c.execute("SELECT * FROM record")
    records = c.fetchall()
    conn.close()
    return records
# --------------------------------------------------------------------------------------------

# creating database
create_database_and_tables()
create_table()

def generate_frames_1(ip):
    camera = cv2.VideoCapture(ip)
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


def generate_frames_2(ip):
    camera = cv2.VideoCapture(ip)
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


def generate_frames_3(ip):
    camera = cv2.VideoCapture(ip)
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


def generate_frames_4(ip):
    camera = cv2.VideoCapture(ip)
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


def retrieve_ip(camera):
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    if camera == 0:
        cursor.execute("""
                SELECT ip1  
                FROM cameras
                LIMIT 1
            """)
    elif camera == 1:
        cursor.execute("""
                SELECT ip2
                FROM cameras
                LIMIT 1
            """)
    elif camera == 2:
        cursor.execute("""
                SELECT ip3 
                FROM cameras
                LIMIT 1
            """)
    elif camera == 3:
        cursor.execute("""
                SELECT ip4  
                FROM cameras
                LIMIT 1
            """)
    else:
        print("Camera limit exceed")

    ip = cursor.fetchone()
    print(ip)  # Fetching one IP address
    conn.close()
    return int(ip[0]) if ip else None


@app.route('/')
def homepage():
    return render_template("login.html")


@app.route('/load', methods=['POST'])
def load():
    username = request.form.get('username')
    password = request.form.get('password')
    # login
    val_1 = login_post(username, password)
    if val_1:
        print("valid")
        current_uuid = get_system_id()
        print(current_uuid)
        val = check_uuid_and_initial_state(current_uuid, username)
        if val == "Load":
            return render_template("load.html")
        elif val == "Live":
            return render_template("live_feed.html")
    else:
        print("invalid")

    # should not login
    return "Invalid"


@app.route('/next_page')
def next_page():
    current_uuid = get_system_id()
    val = check_uuid_and_initial_state(current_uuid)
    if val == "Load":
        return render_template("load.html")
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


@app.route("/pinging", methods=['POST'])
def pinging():
    plc_ip = request.form.get('data_1')
    res = is_pingable(plc_ip)
    if res:
        with open("static/js/db.txt", 'w') as file:
            file.write('1\n')
    else:
        with open("static/js/db.txt", 'w') as file:
            file.write('0\n')
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
    plcip = data.get('plc_ip')
    plcport = data.get('plc_port')
    store_camera_ips(ip1, ip2, ip3, ip4, plcip, plcport)
    print("Ip and plc are stored...........")
    sys_uuid = get_system_id()
    update_initial_state(sys_uuid, 1)
    return jsonify({'success': True})


@app.route('/live_feed_page')
def live_feed_page():
    return render_template("live_feed.html")


@app.route('/live_1')
def live_1():
    ip1 = retrieve_ip(0)
    print(type(ip1))
    print(ip1)
    return Response(generate_frames_1(ip1), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/live_2')
def live_2():
    ip2 = retrieve_ip(1)
    return Response(generate_frames_2(ip2), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/live_3')
def live_3():
    ip3 = retrieve_ip(2)
    return Response(generate_frames_3(ip3), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/live_4')
def live_4():
    ip4 = retrieve_ip(3)
    return Response(generate_frames_4(ip4), mimetype='multipart/x-mixed-replace; boundary=frame')

update_record('Camera 1', '/path/to/screenshot1.png',5)
update_record('Camera 2', '/path/to/screenshot2.png',3)

@app.route('/record')
def record():
    records = fetch_records()
    return render_template('record_template.html', records=records)


if __name__ == "__main__":
    app.run(debug=True)
