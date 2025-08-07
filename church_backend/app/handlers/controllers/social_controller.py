
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from handlers.services import social_service
from models.user import User

def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)

@jwt_required()
def create_thread():
    user = get_current_user()
    data = request.get_json()
    thread = social_service.create_thread(
        user=user,
        title=data["title"],
        body=data["body"],
        is_global=data.get("is_global", False),
        branch_id=data.get("branch_id")
    )
    return jsonify(thread.serialize()), 201

@jwt_required()
def list_threads():
    user = get_current_user()
    threads = social_service.list_threads(user)
    return jsonify([t.serialize() for t in threads]), 200

@jwt_required()
def get_thread(thread_id):
    user = get_current_user()
    thread = social_service.get_thread_by_id(user, thread_id)
    return jsonify(thread.serialize()), 200

@jwt_required()
def add_comment(thread_id):
    user = get_current_user()
    data = request.get_json()
    comment = social_service.add_comment(
        user=user,
        thread_id=thread_id,
        body=data["body"],
        parent_comment_id=data.get("parent_comment_id")
    )
    return jsonify(comment.serialize()), 201

@jwt_required()
def like_thread(thread_id):
    user = get_current_user()
    thread = social_service.like_thread(user, thread_id)
    return jsonify({"message": "Thread liked"}), 200

@jwt_required()
def like_comment(comment_id):
    user = get_current_user()
    comment = social_service.like_comment(user, comment_id)
    return jsonify({"message": "Comment liked"}), 200

@jwt_required()
def get_threads_by_hashtag(tag):
    user = get_current_user()
    threads = social_service.get_threads_by_hashtag(user, tag)
    return jsonify([t.serialize() for t in threads]), 200
