from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from app.models.event_assignment import EventBranchAssignment
from models.event_contribution import EventContribution
from utils.decorators import role_required
from app import db
from app.models.events import Event

event_bp = Blueprint("events", __name__, url_prefix='/event')
def generate_contribution(event, branch_ids):
    
    
    users = User.query.filter(User.branch_id.in_(branch_ids)).all()
    contributions = []
    
    for user in users:
        contributions.append(EventContribution(
            user_id = user.id,
            event_id = event.id,
            status = 'none',
            balance = event.target_amount
        ))
        
    db.session.add_all(contributions)
    
@event_bp.route('/events', methods=['POST'])
@jwt_required()
@role_required(['super-admin', 'admin'])
def create_event():
    data = request.get_json()
    event = Event(**data)
    db.session.add(event)
    db.session.commit()
    
    branch_ids = data.get('branch_ids', [])
    for branch_id in branch_ids:
        assignment = EventBranchAssignment(event_id = event.id, branch_id=branch_id)
        db.session.add(assignment)
        
    generate_contribution(event, branch_ids)
    db.session.commit()
    
    return jsonify({'message':'Event created successfully'})

@event_bp.route('/events', methods=['GET'])
@jwt_required()
def get_events():
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)

    if current_user.role != 'super-admin':
        branch_id = current_user.branch_id
        assigned_event_ids = db.session.query(EventBranchAssignment.event_id)\
            .filter_by(branch_id=branch_id).subquery()
        query = query.filter(
            (Event.is_global == True) |
            (Event.id.in_(assigned_event_ids))
        )
        
    events = query.order_by(Event.start_date.desc()).all()
    return jsonify([event.to_dict() for event in events])