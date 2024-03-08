import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import cv2
import self as self
import wmi as wmi
import pythoncom
import os
from datetime import datetime
from PIL import ImageTk,Image
from tkcalendar import DateEntry
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
    cursor.execute('''CREATE TABLE IF NOT EXISTS records
                      (id INTEGER PRIMARY KEY,
                       camera TEXT,
                       screenshot_location TEXT,
                       timestamp TEXT,
                       No_of_Tyres_Jammed INTEGER(20))''')


    conn.commit()
    conn.close()

def create_table():
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO records (camera, screenshot_location, timestamp, No_of_Tyres_Jammed)
                      VALUES ('Camera 1', 'location1.jpg', '2024-03-08 10:00:00', 3)''')
    cursor.execute('''INSERT INTO records (camera, screenshot_location, timestamp, No_of_Tyres_Jammed)
                      VALUES ('Camera 2', 'location2.jpg', '2024-03-08 10:05:00', 2)''')
    cursor.execute('''INSERT INTO records (camera, screenshot_location, timestamp, No_of_Tyres_Jammed)
                      VALUES ('Camera 3', 'location3.jpg', '2024-03-08 10:10:00', 1)''')
    cursor.execute('''INSERT INTO records (camera, screenshot_location, timestamp, No_of_Tyres_Jammed)
                      VALUES ('Camera 4', 'location4.jpg', '2024-03-08 10:15:00', 4)''')

    conn.commit()
    conn.close()

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
    return ip[0] if ip else None

# ----------------------------------------------------------------------------------------------------------------------
create_database_and_tables()
create_table()

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Apollo Tyres")
        self.geometry("600x400")  # Increased size
        self.frames = {}
        self.login_frame = LoginPage(self)
        self.ip_address_frame = IPAddressPage(self)
        self.welcome_frame = WelcomePage(self)
        self.records_frame = RecordsPage(self)
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
            self.welcome_frame.start_camera_feeds()
        elif frame_name == "records":
            self.login_frame.pack_forget()
            self.ip_address_frame.pack_forget()
            self.welcome_frame.pack_forget()
            self.records_frame.pack(fill='both', expand=True)


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

        camera_url = ip_address
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
        self.master = master

        label = ttk.Label(self, text="Live feed", font=('Helvetica', 16))
        label.grid(row=0, column=0, pady=10)

        # Create a navigation bar frame
        self.nav_bar = tk.Frame(self)
        self.nav_bar.grid(row=0, column=1, padx=10, pady=10)

        # Add "Show Records" button to the navigation bar
        self.show_records_button = ttk.Button(self.nav_bar, text="Show Records", command=self.show_records)
        self.show_records_button.grid(row=0, column=0, pady=10)

        self.frame = tk.Frame(self)
        self.frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Remove the label from the grid
        self.labels = []  # Clear the labels list

        # Get list of video files
        ip1 = retrieve_ip(0)
        ip2 = retrieve_ip(1)
        ip3 = retrieve_ip(2)
        ip4 = retrieve_ip(3)
        video_files = [ip1, ip2, ip3, ip4]

        # Create OpenCV video capture objects for each camera feed
        capture_objects = [cv2.VideoCapture(file) for file in video_files]

        # Create labels for each camera feed and add them to the list
        for i, cap in enumerate(capture_objects):
            label = tk.Label(self.frame)
            label.grid(row=i // 2, column=i % 2, padx=5, pady=5)
            self.labels.append(label)

        # Start threads to update each camera feed
        self.start_camera_feeds(capture_objects)


    def start_camera_feeds(self, capture_objects):
        for label, cap in zip(self.labels, capture_objects):
            t = threading.Thread(target=self.update_image, args=(label, cap))
            t.daemon = True
            t.start()

    def update_image(self, label, cap):
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error reading frame from video source")
                break
            # Resize the frame to fit the label
            frame = cv2.resize(frame, (750, 350))  # Adjust dimensions as needed
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img = ImageTk.PhotoImage(image=img)
            label.config(image=img)
            label.image = img

    def show_records(self):
        self.master.show_frame("records")


# Import DateEntry widget from tkcalendar module

class RecordsPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        label = ttk.Label(self, text="Records", font=('Helvetica', 16))
        label.grid(row=0, column=0, pady=10, columnspan=3)

        # Create a treeview widget to display records
        self.tree = ttk.Treeview(self, columns=("Camera", "Screenshot Location", "Timestamp", "No. of Tyres Jammed"))
        self.tree.grid(row=1, column=0, columnspan=3, sticky="nsew")

        # Add column headings
        self.tree.heading("#0", text="ID")
        self.tree.heading("Camera", text="Camera")
        self.tree.heading("Screenshot Location", text="Screenshot Location")
        self.tree.heading("Timestamp", text="Timestamp")
        self.tree.heading("No. of Tyres Jammed", text="No. of Tyres Jammed")

        # Add vertical scrollbar
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.grid(row=1, column=3, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

        # Add filter button
        self.filter_button = ttk.Button(self, text="Filter", command=self.filter_records)
        self.filter_button.grid(row=2, column=0, pady=10)

        # Create a Combobox for selecting filter criteria
        self.filter_criteria = ttk.Combobox(self, values=["Date", "Month", "Camera"])
        self.filter_criteria.grid(row=2, column=1, pady=10)
        self.filter_criteria.set("Date")  # Set default value

        # Create a DateEntry widget for selecting date
        self.date_entry = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.date_entry.grid(row=2, column=2, pady=10)
        self.date_entry.grid_remove()  # Hide initially

        # Create a Combobox for selecting camera
        self.camera_combobox = ttk.Combobox(self, values=["Camera 1", "Camera 2", "Camera 3", "Camera 4"])
        self.camera_combobox.grid(row=2, column=2, pady=10)
        self.camera_combobox.grid_remove()  # Hide initially

        # Toggle visibility of DateEntry or Combobox based on selected filter criteria
        self.filter_criteria.bind("<<ComboboxSelected>>", self.toggle_filter_options)

    def toggle_filter_options(self, event):
        # Get the selected filter criteria
        filter_criteria = self.filter_criteria.get()

        # Toggle visibility of DateEntry or Combobox based on selected filter criteria
        if filter_criteria == "Date":
            self.date_entry.grid()
            self.camera_combobox.grid_remove()
        elif filter_criteria == "Month":
            self.date_entry.grid()
            self.camera_combobox.grid_remove()
        elif filter_criteria == "Camera":
            self.camera_combobox.grid()
            self.date_entry.grid_remove()

    def filter_records(self):
        # Get the selected filter criteria
        filter_criteria = self.filter_criteria.get()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve records from the database based on the selected filter criteria
        if filter_criteria == "Date":
            selected_date = self.date_entry.get_date().strftime("%Y-%m-%d")
            cursor.execute("SELECT * FROM records WHERE DATE(timestamp) = ?", (selected_date,))
        elif filter_criteria == "Month":
            selected_month = self.date_entry.get_date().strftime("%Y-%m")
            cursor.execute("SELECT * FROM records WHERE strftime('%Y-%m', timestamp) = ?", (selected_month,))
        elif filter_criteria == "Camera":
            selected_camera = int(self.camera_combobox.get().split()[1])
            cursor.execute("SELECT * FROM records WHERE camera = ?", (f"Camera {selected_camera}",))

        records = cursor.fetchall()

        # Clear existing items in the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert filtered records into the treeview
        for record in records:
            self.tree.insert("", "end", text=record[0], values=(record[1], record[2], record[3], record[4]))

        conn.close()


        # Add a button to show records




if __name__ == "__main__":
    app = Application()
    app.mainloop()

