from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from services.mpesa_services import get_mpesa_token
import requests, datetime, base64, os
from models.user import User
from models.logs import ApiLog

mpesa_router = Blueprint('mpesa_router', __name__)

@mpesa_router.route('/stkpush', methods=['POST'])
@jwt_required()
def stk_push():
    user_id = get_jwt_identity()
    data = request.get_json()
    user = User.query.get(user_id)
    
    if user.phone_number != data['phone']:
        return jsonify({
            'error': 'phone number mismatch'
        }), 403
    
    token = get_mpesa_token()
    headers = {
        "Authorization": f"Bearer {token}",
        'Content-Type' : 'application/json'
    }
    
    timestamp = datetime.datetime.utcnow(). strftime("%d%m%Y, %H:%M")
    password = base64.b64decode(
        (os.getenv('MPESA_SHORTCODE')+ os.getenv('MPESA_PASSKEY') + timestamp).encode()
    ).decode()
    
    payload = {
        "BusinessShortCode": os.getenv("MPESA_SHORTCODE"),
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": data.get('amount'),
        "PartyA": data.get('phone'),
        "PartyB": os.getenv("MPESA_SHORTCODE"),
        "PhoneNumber": data.get('phone'),
        "CallBackURL": os.getenv("MPESA_CALLBACK_URL"),
        "AccountReference": f"Event-{data.get('event_id')}",
        "TransactionDesc": "Church Contribution"
    }
    
    stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest" \
        if os.getenv("MPESA_ENV") == "sandbox" else \
        "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    
    res = requests.post(stk_url, json=payload, headers=headers)
    
    ApiLog.log("stk_push", request.json, res.json())
    return jsonify(res.json()), res.status_code


