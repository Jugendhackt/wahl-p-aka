from flask import Flask

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
    return "<p>Hello, World!</p>"
