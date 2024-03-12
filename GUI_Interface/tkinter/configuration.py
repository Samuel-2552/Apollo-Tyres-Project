import ctypes
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import cv2

class LoginPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("Login Page")

        self.username = "Apollo"  # Hardcoded username
        self.password = "ap0110"  # Hardcoded password

        self.create_widgets()

    def create_widgets(self):
        label_username = ttk.Label(self, text="Username:")
        label_username.grid(row=0, column=0, padx=5, pady=5)

        self.entry_username = ttk.Entry(self)
        self.entry_username.grid(row=0, column=1, padx=5, pady=5)

        label_password = ttk.Label(self, text="Password:")
        label_password.grid(row=1, column=0, padx=5, pady=5)

        self.entry_password = ttk.Entry(self, show="*")
        self.entry_password.grid(row=1, column=1, padx=5, pady=5)

        login_button = ttk.Button(self, text="Login", command=self.handle_login)
        login_button.grid(row=2, column=0, columnspan=2, pady=10)

    def handle_login(self):
        entered_username = self.entry_username.get()
        entered_password = self.entry_password.get()

        print("Entered Username:", entered_username)
        print("Entered Password:", entered_password)

        if entered_username == self.username and entered_password == self.password:
            print("Login successful")
            self.destroy()  # Hide the login page
            ip_address_page = IPAddressPage(self.master)
            ip_address_page.pack(fill='both', expand=True)
        else:
            print("Login failed")
            messagebox.showerror("Login Failed", "Invalid username or password.")

class IPAddressPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.count = 0  # Initialize count attribute
        self.list = []
        self.list_plc = []
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
        self.proceed_button = ttk.Button(self, text="Update", command=self.handle_update)
        self.proceed_button.pack(pady=10)

    def handle_update(self):
        # Connect to the database
        if self.count >= 4:
            if len(self.list) == 4:
                conn = sqlite3.connect("config.db")
                cursor = conn.cursor()
                # Get the IP addresses from the entries
                ip_addresses = [entry.get() for entry in self.ip_entries]
                plcip = "172.16.248"  # Hardcoded plcip
                plcport = 5000  # Hardcoded plcport
                # Update the first row of the cameras table with the IP addresses
                cursor.execute("UPDATE cameras SET ip1=?, ip2=?, ip3=?, ip4=?, plcip=?, plcport=? WHERE id=1",
                               (*ip_addresses, plcip, plcport))

                conn.commit()
                conn.close()

                messagebox.showinfo("Update Successful", "IP addresses updated successfully.")

        else:
            messagebox.showerror("IP Failed", "Check the ip address")

    def handle_plc(self, index):
        plc = self.ip_entries[index].get()
        self.list_plc.append(plc)
        print(self.list)
        print(plc)
        self.success_labels[index].config(text="Success", foreground="green")

    def handle_test(self, index):
        print(index)
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
            self.list[index] = ip_address
            print(self.list)
            self.count += 1  # Increment count
            self.success_labels[index].config(text="Success", foreground="green")
        elif content == "0":
            self.success_labels[index].config(text="Failed", foreground="red")
        else:
            print("Database couldn't be read")

def get_screen_resolution():
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Login System")
    width, height = get_screen_resolution()
    root.geometry(f"{width}x{height}+0+0")
    root.state('zoomed')  # Open in fullscreen mode without hiding close, minimize elements
    login_page = LoginPage(root)
    login_page.pack(fill='both', expand=True)
    root.mainloop()
