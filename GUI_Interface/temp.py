import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
import subprocess

class FlaskAppRunner(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Flask App Runner')

        # Button to start Flask app
        start_button = QPushButton('Start Flask App', self)
        start_button.clicked.connect(self.start_flask)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(start_button)

        self.setLayout(layout)

    def start_flask(self):
        subprocess.Popen(["python", "app.py"])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FlaskAppRunner()
    window.show()
    sys.exit(app.exec_())
