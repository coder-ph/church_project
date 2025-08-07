# handlers/services/social_service.py

import re
from app import db
from models.Social import ConversationThread, Comment, Like, Hashtag
from sqlalchemy.orm import joinedload

def extract_hashtags(text):
    return re.findall(r"#(\w+)", text)

def create_thread(user, title, body, is_global, branch_id=None):
    if user.role not in ["superadmin", "admin"]:
        raise PermissionError("You are not allowed to create threads.")

    thread = ConversationThread(
        title=title,
        body=body,
        created_by=user.id,
        branch_id=branch_id if not is_global else None,
        is_global=is_global
    )
    db.session.add(thread)
    db.session.flush()

    hashtags = extract_hashtags(body)
    for tag in hashtags:
        db.session.add(Hashtag(name=tag.lower(), thread_id=thread.id))

    db.session.commit()
    return thread

def list_threads(user):
    query = ConversationThread.query.options(joinedload(ConversationThread.created_by_user))
    if user.role in ["superadmin", "admin"]:
        return query.order_by(ConversationThread.created_at.desc()).all()
    return query.filter(
        (ConversationThread.is_global == True) |
        (ConversationThread.branch_id == user.branch_id)
    ).order_by(ConversationThread.created_at.desc()).all()

def get_thread_by_id(user, thread_id):
    thread = ConversationThread.query.get_or_404(thread_id)
    if user.role in ["superadmin", "admin"]:
        return thread
    if not thread.is_global and thread.branch_id != user.branch_id:
        raise PermissionError("You are not allowed to view this thread.")
    return thread

def add_comment(user, thread_id, body, parent_comment_id=None):
    thread = get_thread_by_id(user, thread_id)
    comment = Comment(user_id=user.id, thread_id=thread.id, body=body, parent_comment_id=parent_comment_id)
    db.session.add(comment)
    db.session.commit()
    return comment

def like_thread(user, thread_id):
    thread = get_thread_by_id(user, thread_id)
    existing_like = Like.query.filter_by(user_id=user.id, thread_id=thread.id).first()
    if not existing_like:
        db.session.add(Like(user_id=user.id, thread_id=thread.id))
        db.session.commit()
    return thread

def like_comment(user, comment_id):
    comment = Comment.query.get_or_404(comment_id)
    existing_like = Like.query.filter_by(user_id=user.id, comment_id=comment.id).first()
    if not existing_like:
        db.session.add(Like(user_id=user.id, comment_id=comment.id))
        db.session.commit()
    return comment

def get_threads_by_hashtag(user, tag):
    query = ConversationThread.query.join(Hashtag).filter(Hashtag.name == tag.lower())
    if user.role not in ["superadmin", "admin"]:
        query = query.filter(
            (ConversationThread.is_global == True) |
            (ConversationThread.branch_id == user.branch_id)
        )
    return query.all()
