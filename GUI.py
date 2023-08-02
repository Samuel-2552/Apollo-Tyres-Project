import sys
import subprocess
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QSizePolicy
from PyQt5.QtWebEngineWidgets import QWebEngineView

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Simple Web Browser")
        self.resize(800, 600)

        # Create the web view widget
        self.webview = QWebEngineView(self)
        self.webview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.webview.urlChanged.connect(self.update_address_bar)  # Connect the urlChanged signal

        # Create the address bar
        self.address_bar = QLineEdit(self)
        self.address_bar.returnPressed.connect(self.load_url)

        # Create the go button
        self.go_button = QPushButton("Go", self)
        self.go_button.clicked.connect(self.load_url)

        # Create a horizontal layout to hold the address bar and go button
        self.address_layout = QHBoxLayout()
        self.address_layout.addWidget(self.address_bar)
        self.address_layout.addWidget(self.go_button)

        # Create a vertical layout to hold the address layout and web view
        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.address_layout)
        self.main_layout.addWidget(self.webview)

        # Create a central widget to set the layout
        central_widget = QWidget(self)
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

        # Create the menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Load Google by default
        self.load_url("http://127.0.0.1:5000")

    def load_url(self, url=None):
        if not url:
            url = self.address_bar.text()
        if "http://" not in url and "https://" not in url:
            url = "http://" + url
        self.webview.setUrl(QUrl(url))

    def update_address_bar(self, url):
        self.address_bar.setText(url.toString())



if __name__ == "__main__":
    # Run the Flask app in a separate process
    flask_process = subprocess.Popen(["python", "app.py"])

    app = QApplication(sys.argv)
    browser = BrowserWindow()
    browser.show()
    sys.exit(app.exec_())
