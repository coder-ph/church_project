from app import db
from datetime import datetime

class Hashtag(db.Model):
    __tablename__ = 'hashtags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    thread_id = db.Column(db.Integer, db.ForeignKey('conversation_threads.id', ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    thread = db.relationship("ConversationThread", back_populates="hashtags")

    def __repr__(self):
        return f"<Hashtag #{self.name}>"
