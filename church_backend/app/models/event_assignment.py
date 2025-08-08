from app.extensions import db

class EventBranchAssignment(db.Model):
    __tablename__ = 'event_branch_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    
    event = db.relationship('Event', back_populates='assignments')
    branch = db.relationship('Branch')