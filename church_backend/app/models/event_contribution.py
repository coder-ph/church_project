from datetime import datetime
from app.extensions import db
from enum import Enum
import uuid
from sqlalchemy.dialects.postgresql import UUID

class ContributionStatus(Enum):
    NOT_STARTED = "Not Started"
    PARTIAL = 'Partial'
    COMPLETE = 'Complete'
class EventContribution(db.Model):
    __tablename__ = 'event_contributions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    amount_expected = db.Column(db.Float, nullable=False)
    amount_paid = db.Column(db.DateTime, default=datetime.utcnow)
    balance = db.Column(db.Float, default=0.0)
    
    status = db.Column(db.Enum(ContributionStatus), default=ContributionStatus.NOT_STARTED)
    
    user = db.relationship('User', backref='contributions')
    event = db.relationship('Event', backref='contributions')
    
    def update_payment(self, amount):
        self.amount_paid +=amount
        self.balance = self.amount_expected - self.amount_paid
        
        if self.amount_paid == 0:
            self.status = ContributionStatus.NOT_STARTED
        elif 0 < self.amount_paid<self.amount_expected:
            self.status = ContributionStatus.PARTIAL
            
        else:
            self.status = ContributionStatus.COMPLETE