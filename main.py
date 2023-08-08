# main.py
import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication
from GUI import BrowserWindow  # Replace 'GUI' with the actual name of your Python GUI script

def run_flask_app():
    # Change directory to 'data_folder' where your Flask app resides
    os.chdir('data_folder')

    # Run Flask app as a background process with suppressed console
    subprocess.Popen([sys.executable, 'app.py'], creationflags=subprocess.CREATE_NO_WINDOW)

if getattr(sys, 'frozen', False):
    # If the application is run as a standalone executable, adjust the current working directory
    # to make sure the 'data_folder' is accessible.
    os.chdir(sys._MEIPASS)


if __name__ == "__main__":
    # Run Flask app in the background
    run_flask_app()

    # Run your GUI application
    app = QApplication(sys.argv)
    browser = BrowserWindow()
    browser.show()
    sys.exit(app.exec_())
