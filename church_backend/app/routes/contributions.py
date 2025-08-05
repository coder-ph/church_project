from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import role_required
from app.models.event_contribution import EventContribution
from app import db
import Logger
logger = Logger()

event_contrib_bp = Blueprint("event_contributions", __name__, url_prefix='/event_contributions')
@event_contrib_bp('/my-contributions', methods=['GET'])
@jwt_required()
def get_my_contributions():
    current_user = get_jwt_identity()
    contributions = EventContribution.query.filter_by(user_id=current_user['id']).all()
    try:
        if contributions:
            return jsonify([{
        "event_title": contrib.event.title,
        "amount_expected": contrib.amount_expected,
        "amount_paid": contrib.amount_paid,
        "balance": contrib.balance,
        "status": contrib.status.value 
            } for contrib in contributions])
            
    except Exception as e:
        logger.error("an error occured", e)
        
@event_contrib_bp.route('/events/<int:event_id>/contributions', methods=['GET'])
@jwt_required()
@role_required("super-admin", 'admin')
def get_event_contributions(event_id):
    contributions = EventContribution.query.filter_by(event_id=event_id).all()
    return jsonify([{
        "user_id": contrib.user_id,
        "amount_expected": contrib.amount_expected,
        "amount_paid": contrib.amount_paid,
        "balance": contrib.balance,
        "status": contrib.status.value
    } for contrib in contributions])