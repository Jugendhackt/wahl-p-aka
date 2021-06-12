from flask import Blueprint, jsonify

api_blueprint = Blueprint('api', __name__)


@api_blueprint.route("/")
def api_home():
    return jsonify({'msg': 'Hello World!'})