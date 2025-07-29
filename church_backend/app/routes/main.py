from flask import Blueprint, jsonify

main_pb = Blueprint("main", __name__)

@main_pb.route("/")
def home():
    return jsonify({"message: Church Backend Running"})