from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QTimer
import sys


class WebBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Simple Web Browser")
        self.setGeometry(100, 100, 1024, 768)

        # Create a central widget to display web content
        self.web_view = QWebEngineView(self)
        self.setCentralWidget(self.web_view)

        # Set a default URL to load
        default_url = "https://www.google.com"
        self.web_view.setUrl(QUrl(default_url))

        # Create a non-editable address bar
        self.address_bar = QLineEdit(self)
        self.address_bar.setReadOnly(True)
        self.address_bar.setText(default_url)
        self.addToolBar("AddressBar").addWidget(self.address_bar)

        # Create a timer to open the password window after 2 seconds
        QTimer.singleShot(2000, self.open_password_window)

    def open_password_window(self):
        password_window = PasswordWindow(self)
        password_window.show()
        self.setEnabled(False)

class PasswordWindow(QMainWindow):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        self.setWindowTitle("Password Window")
        self.setGeometry(200, 200, 400, 300)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setGeometry(100, 100, 200, 30)

        submit_button = QAction("Submit", self)
        submit_button.triggered.connect(self.check_password)

        self.toolbar = self.addToolBar("Toolbar")
        self.toolbar.addAction(submit_button)

    def check_password(self):
        entered_password = self.password_input.text()
        if entered_password == "password":
            self.close()
            self.main_window.setEnabled(True)
        else:
            QMessageBox.warning(self, "Incorrect Password", "Please enter the correct password.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = WebBrowser()
    browser.show()
    sys.exit(app.exec_())