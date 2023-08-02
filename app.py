from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Placeholder for the password (you can implement a more secure solution)
PASSWORD = "1234"

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

if __name__ == "__main__":
    app.run(debug=True)
