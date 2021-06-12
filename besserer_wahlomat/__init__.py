from flask import Flask, render_template

from api import api_blueprint

app = Flask(__name__)

app.register_blueprint(api_blueprint, url_prefix='/api')


@app.route("/main/")
@app.route
def hello_world():
    return render_template("main.html"), render_template("question_site.html"), render_template("mystyle.css")
