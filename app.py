import cv2
from flask import Flask, render_template, request, redirect, Response

app = Flask(__name__)

# Placeholder for the password (you can implement a more secure solution)
PASSWORD = "1234"

# OpenCV VideoCapture object to access the camera
camera = cv2.VideoCapture(1)  # Use '0' for the default camera, change to other numbers for different cameras if available

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


@app.route("/", methods=["GET", "POST"])
def home():
    error_message = None

    if request.method == "POST":
        entered_password = request.form.get("password")
        if entered_password == PASSWORD:
            return redirect("/success")
        else:
            error_message = "Invalid password. Please try again."

    return render_template("home.html", error_message=error_message)

@app.route("/success")
def success():
    return render_template("success.html")

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)
