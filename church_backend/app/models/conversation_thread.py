
from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID

class ConversationThread(db.Model):
    __tablename__ = 'conversation_threads'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    hashtags = db.Column(db.ARRAY(db.String), default=[])
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"), nullable=False)

    created_by_user = db.relationship("User", backref="threads")
    branch = db.relationship("Branch", backref="threads")
    
    hashtags = db.relationship("Hashtag", back_populates="thread", cascade="all, delete-orphan")
