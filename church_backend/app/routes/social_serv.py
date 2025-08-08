from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.conversation_thread import ConversationThread
from app.models.comment import Comment
from app.models.like import Like
from app.models.hashtag import Hashtag
from app.models.user import User
from app.models.branch import Branch

social_bp = Blueprint('social', __name__, url_prefix='/social')

def get_user():
    identity = get_jwt_identity()
    return User.query.get(identity['id'])

@social_bp.route('/threads', methods=['POST'])
@jwt_required()
def create_thread():
    user = get_user()
    data = request.get_json()

    thread = ConversationThread(
        title=data['title'],
        body=data['body'],
        created_by=user.id,
        branch_id=data.get('branch_id') if user.role == 'member' else data.get('branch_id') or None
    )

    db.session.add(thread)
    db.session.commit()

    # Handle hashtags
    hashtags = data.get('hashtags', [])
    for tag in hashtags:
        h = Hashtag(name=tag, thread_id=thread.id)
        db.session.add(h)

    db.session.commit()
    return jsonify(message="Thread created", thread_id=thread.id), 201

@social_bp.route('/threads', methods=['GET'])
@jwt_required()
def list_threads():
    user = get_user()
    if user.role in ['admin', 'superadmin']:
        threads = ConversationThread.query.all()
    else:
        threads = ConversationThread.query.filter_by(branch_id=user.branch_id).all()

    response = []
    for thread in threads:
        response.append({
            "id": thread.id,
            "title": thread.title,
            "body": thread.body,
            "created_by": thread.created_by,
            "branch_id": thread.branch_id,
            "hashtags": [h.name for h in thread.hashtags],
            "created_at": thread.created_at
        })
    return jsonify(threads=response), 200

@social_bp.route('/threads/<int:thread_id>/comment', methods=['POST'])
@jwt_required()
def comment_on_thread(thread_id):
    user = get_user()
    data = request.get_json()
    body = data['body']

    thread = ConversationThread.query.get_or_404(thread_id)
    if user.role == 'member' and thread.branch_id != user.branch_id:
        return jsonify(message="Not allowed to comment on this thread"), 403

    comment = Comment(
        user_id=user.id,
        body=body,
        thread_id=thread.id,
        parent_comment_id=data.get('parent_comment_id')
    )
    db.session.add(comment)
    db.session.commit()

    return jsonify(message="Comment added"), 201

@social_bp.route('/comments/<int:comment_id>/like', methods=['POST'])
@jwt_required()
def like_comment(comment_id):
    user = get_user()
    like = Like.query.filter_by(user_id=user.id, comment_id=comment_id).first()
    if like:
        return jsonify(message="Already liked"), 400

    new_like = Like(user_id=user.id, comment_id=comment_id)
    db.session.add(new_like)
    db.session.commit()
    return jsonify(message="Liked comment"), 200

@social_bp.route('/threads/<int:thread_id>/like', methods=['POST'])
@jwt_required()
def like_thread(thread_id):
    user = get_user()
    like = Like.query.filter_by(user_id=user.id, thread_id=thread_id).first()
    if like:
        return jsonify(message="Already liked"), 400

    new_like = Like(user_id=user.id, thread_id=thread_id)
    db.session.add(new_like)
    db.session.commit()
    return jsonify(message="Liked thread"), 200

@social_bp.route('/hashtags/<string:tag>', methods=['GET'])
@jwt_required()
def search_by_hashtag(tag):
    user = get_user()
    hashtag_matches = Hashtag.query.filter_by(name=tag).all()
    thread_ids = [h.thread_id for h in hashtag_matches]

    if user.role in ['admin', 'superadmin']:
        threads = ConversationThread.query.filter(ConversationThread.id.in_(thread_ids)).all()
    else:
        threads = ConversationThread.query.filter(ConversationThread.id.in_(thread_ids), ConversationThread.branch_id == user.branch_id).all()

    response = []
    for thread in threads:
        response.append({
            "id": thread.id,
            "title": thread.title,
            "body": thread.body,
            "created_by": thread.created_by,
            "branch_id": thread.branch_id,
            "hashtags": [h.name for h in thread.hashtags],
            "created_at": thread.created_at
        })
    return jsonify(threads=response), 200
