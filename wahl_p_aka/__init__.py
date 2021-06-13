import flask
from flask import Flask

app = Flask(__name__)

try:
    app.config.from_pyfile('application.cfg')
except FileNotFoundError:
    print("WARNING: No configuration file found.")
    app.config.from_pyfile('application.cfg.example')

from .database import db, PollTopic, Poll, Party


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
    db_polltopics = db.session.query(PollTopic).filter(PollTopic.id.in_(topic_ids))
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
    formdata = flask.request.form
    polls = {}
    for item in formdata.items():
        if item[1] in ("yes", "no", "abstain") and "radio" in item[0]:
            polls[int(item[0].split("_")[1])] = item[1]

    party_acceptence = {}
    parties = Party.query.all()
    for party in parties:
        party_acceptence[party.id] = {
            "short_name": party.short_name,
            "full_name": party.full_name,
            "color": party.color,
            "percent": 0
        }
    number_polls = 0
    for poll in polls.items():
        db_poll = db.session.query(Poll).filter(Poll.id == poll[0]).first()
        if poll[1] != "abstain":
            number_polls += 1
            for party_vote in db_poll.party_votes:
                total_party_people = party_vote.yes + party_vote.no + party_vote.absent + party_vote.abstain
                if poll[1] == "yes":
                    party_acceptence[party_vote.party_id]['percent'] += ((party_vote.yes / total_party_people) * 100)
                elif poll[1] == "no":
                    party_acceptence[party_vote.party_id]['percent'] += ((party_vote.no / total_party_people) * 100)

    result = []
    for party in party_acceptence.items():
        result.append({
            "short_name": party[1]['short_name'],
            "full_name": party[1]['full_name'],
            "percent": party[1]['percent'] / number_polls,
            "color": party[1]['color'],
        })
    return flask.render_template("result.html", result=result)
