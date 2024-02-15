import cv2
import os
from flask import Flask, render_template, request, redirect, Response, jsonify

app = Flask(__name__)

camera = cv2.VideoCapture(0)  # Use '0' for the default camera, change to other numbers for different cameras if available


def generate_frames():
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


@app.route('/')
def homepage():
    return render_template("login.html")


@app.route('/load', methods=['POST'])
def load():
    username = request.form.get('username')
    password = request.form.get('password')
    return render_template("load.html")


@app.route('/signup_page')
def signup_page():
    return render_template("signup.html")


@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')
    return render_template("load.html")


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


@app.route("/live_feed")
def live_feed():
    return render_template("live_feed.html")


@app.route('/live')
def live():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)
