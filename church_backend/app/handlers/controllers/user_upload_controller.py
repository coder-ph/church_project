from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from services.user_upload_service import process_user_upload

upload_users_bp = Blueprint("upload_users", __name__)

@upload_users_bp.route("/upload-users", methods=["POST"])
@jwt_required()
def upload_users():
    user_id = get_jwt_identity()
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    summary = process_user_upload(file, user_id)
    return jsonify(summary), 200