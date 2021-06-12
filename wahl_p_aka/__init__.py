from flask import Flask, render_template

from wahl_p_aka.api import api_blueprint

app = Flask(__name__)

try:
    app.config.from_pyfile('application.cfg')
except FileNotFoundError:
    print("WARNING: No configuration file found.")
    app.config.from_pyfile('application.cfg.example')

from .database import db

app.register_blueprint(api_blueprint, url_prefix='/api')


@app.route("/")
def hello_world():
    return render_template("main.html")


@app.route("/info")
def better_world():
    return render_template("question_site.html")
