import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import cv2
import self as self
import wmi as wmi
import pythoncom
import os
# Creating database ----------------------------------------------------------------------------------------------------

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

# def create_table():
#     conn = sqlite3.connect('config.db')
#     c = conn.cursor()
#     c.execute('''CREATE TABLE IF NOT EXISTS record
#                  (camera TEXT, screenshot_location TEXT, timestamp TEXT,No_of_Tyres_Jammed INTEGER(20))''')
#     conn.commit()
#     conn.close()

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

# ----------------------------------------------------------------------------------------------------------------------
create_database_and_tables()
# create_table()

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Navigation Example")
        self.geometry("600x400")  # Increased size

        self.frames = {}

        self.login_frame = LoginPage(self)
        self.ip_address_frame = IPAddressPage(self)
        self.welcome_frame = WelcomePage(self)
        self.show_frame("login")

    def show_frame(self, frame_name):
        if frame_name == "login":
            self.login_frame.pack(fill='both', expand=True)
            self.ip_address_frame.pack_forget()
            self.welcome_frame.pack_forget()
        elif frame_name == "ip_address":
            self.login_frame.pack_forget()
            self.ip_address_frame.pack(fill='both', expand=True)
            self.welcome_frame.pack_forget()
        elif frame_name == "welcome":
            self.login_frame.pack_forget()
            self.ip_address_frame.pack_forget()
            self.welcome_frame.pack(fill='both', expand=True)

class LoginPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        label = ttk.Label(self, text="Login Page", font=('Helvetica', 16))  # Increased font size
        label.pack(pady=10)

        username_label = ttk.Label(self, text="Username:")
        username_label.pack()
        self.username_entry = ttk.Entry(self)
        self.username_entry.pack()

        password_label = ttk.Label(self, text="Password:")
        password_label.pack()
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack()

        self.login_button = ttk.Button(self, text="Login", command=self.handle_login)
        self.login_button.pack(pady=10)

    def handle_login(self):
        # Your login logic goes here
        # For now, I'm just simulating successful login
        # Set to True if login successful, else set to False
        username = self.username_entry.get()  # Retrieve username
        password = self.password_entry.get()  # Retrieve password
        print("Username:", username)
        print("Password:", password)
        login_status = login_post(username, password)
        # username and password stored in database
        if login_status:
            messagebox.showinfo("Login Successful", "Welcome, " + username + "!")
            current_uuid = get_system_id()
            print(current_uuid)
            val = check_uuid_and_initial_state(current_uuid, username)
            if val == "Load":
                self.master.show_frame("ip_address")
            elif val == "Live":
                self.master.show_frame("welcome")
            else:
                print("Problem in database or getting ip ")

        else:
            print("invalid username and password")
            messagebox.showerror("Login Failed", "Invalid username or password.")


class IPAddressPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.count = 0  # Initialize count attribute
        self.list = []
        label = ttk.Label(self, text="IP Address Page", font=('Helvetica', 16))  # Increased font size
        label.pack(pady=10)

        ip_frame = ttk.Frame(self)
        ip_frame.pack(pady=10)

        ip_labels = ["IP Address 1:", "IP Address 2:", "IP Address 3:", "IP Address 4:"]
        self.ip_entries = []
        self.success_labels = []  # Store success labels

        for i in range(4):
            ip_label = ttk.Label(ip_frame, text=ip_labels[i])
            ip_label.grid(row=i, column=0, padx=5, pady=5)

            ip_entry = ttk.Entry(ip_frame)
            ip_entry.grid(row=i, column=1, padx=5, pady=5)
            self.ip_entries.append(ip_entry)

            test_button = ttk.Button(ip_frame, text="Test", command=lambda i=i: self.handle_test(i))
            test_button.grid(row=i, column=2, padx=5, pady=5)

            # Create and pack success labels initially empty
            success_label = ttk.Label(ip_frame, text="")
            success_label.grid(row=i, column=3, padx=5, pady=5)
            self.success_labels.append(success_label)

        # Display success message
        self.proceed_button = ttk.Button(self, text="Proceed", command=self.handle_proceed)
        self.proceed_button.pack(pady=10)

    def handle_proceed(self):
        # Your proceed logic goes here
        # For now, I'm just simulating successful proceed
        # Set to True if proceed successful, else set to False
        if self.count >= 4:
            if len(self.list) == 4:
                ip1 = str(self.list[0])
                ip2 = str(self.list[1])
                ip3 = str(self.list[2])
                ip4 = str(self.list[3])
                plcip = 172
                plcport = 5000
                store_camera_ips(ip1, ip2, ip3, ip4, plcip, plcport)
                sys_uuid = get_system_id()
                update_initial_state(sys_uuid, 1)

            self.master.show_frame("welcome")
        else:
            messagebox.showerror("IP Failed", "Check the ip address")

    def handle_test(self, index):
        ip_address = self.ip_entries[index].get()  # Get the IP address from the entry
        print("Testing IP:", ip_address)

        # Initialize the list with empty strings if it hasn't been initialized yet
        if not self.list:
            self.list = [""] * 4

        camera_url = int(ip_address)
        cap = cv2.VideoCapture(camera_url)
        print(self.count)

        while True:
            ret, frame = cap.read()

            if ret:
                with open("db.txt", 'w') as file:
                    file.write('1\n')
                    break
            else:
                with open("db.txt", 'w') as file:
                    file.write('0\n')
                    break

        with open("db.txt", 'r') as file:
            content = file.read().strip()

        if content == "1":
            self.list[self.count] = ip_address
            print(self.list)
            self.count += 1  # Increment count
            self.success_labels[index].config(text="Success", foreground="green")
        elif content == "0":
            self.success_labels[index].config(text="Failed", foreground="red")
        else:
            print("Database couldn't be read")


class WelcomePage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        label = ttk.Label(self, text="Live feed", font=('Helvetica', 16))  # Increased font size
        label.pack(pady=10)

        welcome_label = ttk.Label(self, text="Welcome!", font=('Helvetica', 12))  # Increased font size
        welcome_label.pack(pady=10)

if __name__ == "__main__":
    app = Application()
    app.mainloop()

