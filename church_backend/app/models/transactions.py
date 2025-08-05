from app import db
import datetime

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String, unique=True, nulable=False)
    method = db.Column(db.String, nullable=False)
    amount = db.column(db.Float, nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    status = db.Column(db.String, default='PENDING')
    created_at = db.Column(db.datetime, default=datetime.now())