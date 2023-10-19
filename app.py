"""MAIN FLASK PROJECT"""

from flask import (
    Flask,
    render_template,
    redirect,
    request
)
from config import Config

app = Flask(__name__)

app.config.from_object(Config)

@app.route("/sakums", methods = ["GET", "POST"])
@app.route("/", methods = ["GET", "POST"])
def index():
    if request.method == "POST":
        ...
    else:
        return render_template("home.html")


if app.config["FLASK_ENV"] == 'development':
    if __name__ == "__main__":
        app.run(debug=True)