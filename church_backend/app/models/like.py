
from app.extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID

class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    thread_id = db.Column(db.Integer, db.ForeignKey("conversation_threads.id"), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="likes")
    thread = db.relationship("ConversationThread", backref="likes")
    comment = db.relationship("Comment", backref="likes")
