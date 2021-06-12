from flask import Flask

from wahl_p_aka.api import api_blueprint

app = Flask(__name__)

app.register_blueprint(api_blueprint, url_prefix='/api')


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
