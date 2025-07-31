from flask import Blueprint, jsonify, request
from models.branch import Branch
from app import db
from utils.decorators import role_required

branch_bp = Blueprint("branch", __name__, url_prefix='/branches')

@branch_bp.route('/', methods=['POST'])
@role_required('super-admin')
def create_branch():
    data = request.get_json()
    branch = Branch(**data)
    branch_check = Branch.query.filter_by(name=data['name']).first()
    try:
        if branch_check:
            return jsonify(message="Branch already exist"), 422
        else:
            db.session.add(branch)
            db.session.commit()
            return jsonify(message="Branch created successfully"), 201
        
    except:
        return jsonify(message='An error occured please try again')
