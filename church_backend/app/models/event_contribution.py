from datetime import datetime
from app import db

class EventContribution(db.Model):
    __tablename__ = 'event_contributions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    
    amount_paid = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User')
    event = db.relationship('Event')