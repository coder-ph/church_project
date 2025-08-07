from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String, unique=True, nullable=False)
    method = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    
    status = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='transactions')
    event = db.relationship('Event', backref='transactions')
