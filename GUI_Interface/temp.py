import tkinter as tk
from tkinter import ttk

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
        login_successful = True

        if login_successful:
            self.master.show_frame("ip_address")

class IPAddressPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

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
        proceed_successful = True
        if proceed_successful:
            self.master.show_frame("welcome")

    def handle_test(self, index):
        ip_address = self.ip_entries[index].get()  # Corrected typo here
        print("Testing IP:", ip_address)
        # Perform test here, currently just print the IP address

        # Update success label
        self.success_labels[index].config(text="Success")  # Display success message

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
