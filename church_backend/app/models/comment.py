# models/comment.py

from app.extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    thread_id = db.Column(db.Integer, db.ForeignKey("conversation_threads.id"), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("comments.id"), nullable=True)

    user = db.relationship("User", backref="comments")
    thread = db.relationship("ConversationThread", backref="comments")
    replies = db.relationship("Comment", backref=db.backref("parent", remote_side=[id]), lazy="dynamic")
