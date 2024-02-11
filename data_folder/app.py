import cv2
from ultralytics import YOLO
from flask import Flask, render_template, request, redirect, Response

app = Flask(__name__)

# Placeholder for the password (you can implement a more secure solution)
PASSWORD = "1234"

model = YOLO('data_folder/static/assets/yolo_125epochs.pt')
# OpenCV VideoCapture object to access the camera
camera = cv2.VideoCapture(2)  # Use '0' for the default camera, change to other numbers for different cameras if available

def generate_frames():
    while camera.isOpened():
        # Read a frame from the video
        success, frame = camera.read()

        if success:
            # Run YOLOv8 inference on the frame
            results = model(frame)

            # Visualize the results on the frame
            annotated_frame = results[0].plot()

            # Convert the frame to JPEG format
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
        
            annotated_frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + annotated_frame + b'\r\n')

            
    


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

@app.route("/test")
def test():
    return render_template("test.html")

@app.route("/success")
def success():
    return render_template("success.html")

@app.route('/video')
def video():
    return render_template("video.html")

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run('0.0.0.0', debug=True)
