from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
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

        # Create an address bar
        self.address_bar = QLineEdit(self)
        self.address_bar.returnPressed.connect(self.navigate_to_url)
        self.addToolBar("AddressBar").addWidget(self.address_bar)

        # Create navigation actions
        nav_bar = self.addToolBar("Navigation")
        nav_bar.addAction("Back", self.navigate_back)
        nav_bar.addAction("Forward", self.navigate_forward)
        nav_bar.addAction("Refresh", self.refresh)

        # Set a default URL to load
        default_url = "https://www.example.com"
        self.web_view.setUrl(QUrl(default_url))

    def navigate_to_url(self):
        url = self.address_bar.text()
        self.web_view.setUrl(QUrl(url))

    def navigate_back(self):
        self.web_view.back()

    def navigate_forward(self):
        self.web_view.forward()

    def refresh(self):
        self.web_view.reload()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = WebBrowser()
    browser.show()
    sys.exit(app.exec_())
