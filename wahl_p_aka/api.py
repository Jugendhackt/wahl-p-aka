import flask

from wahl_p_aka.database import Poll, PollTopic, db

api_blueprint = flask.Blueprint('api', __name__)


@api_blueprint.route("/")
def api_home():
    return flask.jsonify({'msg': 'Hello World!'})


@api_blueprint.route("/polls", methods=['POST'])
def api_get_polls():
    data = flask.request.json

    if data.get('topics') is None:
        return "Request is bad formatted.", 400
    elif len(data['topics']) == 0:
        return "Request is bad formatted.", 400

    polltopics = []
    db_polltopics = db.session.query(PollTopic).filter(PollTopic.aw_id.in_(data['topics']))
    for row in db_polltopics:
        if len(row.children) != 0:
            for child in row.children:
                polltopics.append(child.id)
        polltopics.append(row.id)

    polls = db.session.query(Poll).filter(
        Poll.topics.any(PollTopic.id.in_(polltopics))
    )
    response = []
    for row in polls:
        response.append({
            "id": row.id,
            "title": row.title,
            "abstract": row.abstract,
            "date": row.date
        })
    return flask.jsonify(response)

