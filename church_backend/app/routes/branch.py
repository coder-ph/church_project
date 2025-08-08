from flask import Blueprint, jsonify, request
from app.models.branch import Branch
from app import db
from app.utils.decorators import role_required

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
    
@branch_bp.route('/', methods=['GET'])
@role_required('super-admin','admin')
def get_branches():
    branches = Branch.query.all()
    return jsonify({'id':b.id, 'name':b.name} for b in branches)

@branch_bp.route('/<int:branch_id>', methods=['PUT'])
@role_required('super-admin')
def branch_update(branch_id):
    branch = Branch.query.get_or_404(branch_id)
    data = request.get_json()

    branch.name = data.get('name', branch.name)
    branch.location = data.get('location', branch.location)
    branch.timezone =data.get('timezone', branch.timezone)

    db.session.commit()
    return jsonify(message="Branch updated successfully")
