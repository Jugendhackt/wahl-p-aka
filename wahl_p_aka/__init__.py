from flask import Flask
import flask

app = Flask(__name__)

try:
    app.config.from_pyfile('application.cfg')
except FileNotFoundError:
    print("WARNING: No configuration file found.")
    app.config.from_pyfile('application.cfg.example')

from .database import db, PollTopic, Poll


@app.route("/")
def start_site():
    polltopics = PollTopic.query.all()
    return flask.render_template("start.html", topics=polltopics)


@app.route("/question", methods=['post'])
def question_site():
    formdata = flask.request.form
    topic_ids = []
    for item in formdata.items():
        if item[1] == "on" and "checkbox" in item[0]:
            topic_ids.append(item[0].split("_")[1])

    polltopics = []
    db_polltopics = db.session.query(PollTopic).filter(PollTopic.aw_id.in_(topic_ids))
    for row in db_polltopics:
        if len(row.children) != 0:
            for child in row.children:
                polltopics.append(child.id)
        polltopics.append(row.id)

    polls = db.session.query(Poll).filter(
        Poll.topics.any(PollTopic.id.in_(polltopics))
    )
    questions = []
    for row in polls:
        questions.append({
            "id": row.id,
            "title": row.title,
            "abstract": row.abstract,
            "date": row.date
        })
    return flask.render_template("question_site.html", questions=questions)


@app.route("/result", methods=['post'])
def result_site():
    polltopics = PollTopic.query.all()
    result=[
        {
            "short_name": "SPD",
            "long_name": "Spaßpartei Deutschlands",
            "percent": 20
        },
        {
            "short_name": "CDU",
            "long_name": "Christliche Deutsche Unpartei",
            "percent": 10
        }
    ]
    return flask.render_template("result.html", result=result)
