from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.extensions import db
from app.services.mpesa_services import get_mpesa_token
from app.models.transactions import Transaction
from app.models.logs import ApiLog
import requests
import datetime
import base64
import os
import uuid
from threading import Thread
import time
import json

mpesa_bp = Blueprint('mpesa_router', __name__)

# In-memory storage for callbacks (for testing)
callback_store = {}

def make_mpesa_request(url, payload, headers=None):
    """Helper function to make M-Pesa API requests with retry logic"""
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, headers=headers or {}, timeout=30)
            
            # Handle rate limiting
            if response.status_code == 429:
                wait_time = min(30, (attempt + 1) * retry_delay)
                print(f"Rate limited. Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue
                
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed (attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    return None

@mpesa_bp.route('/stkpush', methods=['POST'])
# @jwt_required()
def stk_push():
    data = request.get_json()
    transaction_ref = str(uuid.uuid4())
    
    # Get token with proper error handling
    token_response = get_mpesa_token()
    if not token_response or 'access_token' not in token_response:
        return jsonify({"error": "Failed to get M-Pesa token"}), 500
        
    token = token_response['access_token']
    
    headers = {
        "Authorization": f"Bearer {token}",
        'Content-Type': 'application/json'
    }

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    raw_password = os.getenv('MPESA_SHORTCODE') + os.getenv('MPESA_PASSKEY') + timestamp
    password = base64.b64encode(raw_password.encode()).decode()

    callback_url = f"https://7f64cf94b0c4.ngrok-free.app/callback?ref={transaction_ref}"

    payload = {
        "BusinessShortCode": os.getenv("MPESA_SHORTCODE"),
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": data.get('amount'),
        "PartyA": data.get('phone'),
        "PartyB": os.getenv("MPESA_SHORTCODE"),
        "PhoneNumber": data.get('phone'),
        "CallBackURL": callback_url,
        "AccountReference": f"Event-{data.get('event_id')}",
        "TransactionDesc": "Church Contribution"
    }

    stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest" \
        if os.getenv("MPESA_ENV") == "sandbox" else \
        "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    res = make_mpesa_request(stk_url, payload, headers)
    if not res:
        return jsonify({"error": "Failed to initiate STK push"}), 500

    res_data = res.json()
    ApiLog.log("stk_push", request.json, res_data)

    print("\n--- STK Push Response ---")
    print(res_data)

    if res.status_code == 200 and res_data.get("ResponseCode") == "0":
        # Create transaction record
        transaction = Transaction(
            transaction_id=transaction_ref,
            method="MPESA",
            amount=data.get("amount"),
            status="PENDING",
            phone_number=data.get('phone'),
            checkout_request_id=res_data.get("CheckoutRequestID"),
            merchant_request_id=res_data.get("MerchantRequestID"),
        )
        db.session.add(transaction)
        db.session.commit()

        # Start verification in background with app context
        app = current_app._get_current_object()
        Thread(
            target=verify_transaction_status,
            args=(app, res_data.get("CheckoutRequestID"), transaction_ref)
        ).start()

    return jsonify({
        "stk_push_response": res_data,
        "transaction_ref": transaction_ref,
        "callback_url": callback_url,
        "message": "Check your phone to complete payment."
    }), res.status_code

def verify_transaction_status(app, checkout_request_id, transaction_ref, max_retries=5):
    """Verify transaction status with proper app context and rate limiting"""
    with app.app_context():
        retry_delays = [5, 10, 15, 30, 60]  # Progressive delays
        
        for attempt in range(max_retries):
            try:
                time.sleep(retry_delays[attempt])
                
                token_response = get_mpesa_token()
                if not token_response or 'access_token' not in token_response:
                    print("Failed to get token for verification")
                    continue
                    
                token = token_response['access_token']
                headers = {"Authorization": f"Bearer {token}"}
                
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                password = base64.b64encode(
                    (os.getenv("MPESA_SHORTCODE") + os.getenv("MPESA_PASSKEY") + timestamp).encode()
                ).decode()

                payload = {
                    "BusinessShortCode": os.getenv("MPESA_SHORTCODE"),
                    "Password": password,
                    "Timestamp": timestamp,
                    "CheckoutRequestID": checkout_request_id
                }

                query_url = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query" \
                    if os.getenv("MPESA_ENV") == "sandbox" else \
                    "https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query"

                response = make_mpesa_request(query_url, payload, headers)
                if not response:
                    continue
                    
                response_data = response.json()
                print(f"\n--- Transaction Query Attempt {attempt + 1} ---")
                print(response_data)

                transaction = Transaction.query.filter_by(
                    checkout_request_id=checkout_request_id
                ).first()
                
                if not transaction:
                    print("Transaction not found in database!")
                    continue

                if response_data.get("ResultCode") == "0":
                    # Success case
                    transaction.status = "SUCCESS"
                    if "CallbackMetadata" in response_data:
                        metadata = response_data["CallbackMetadata"]["Item"]
                        parsed = {
                            "amount": next(item['Value'] for item in metadata if item['Name'] == "Amount"),
                            "mpesa_receipt": next(item['Value'] for item in metadata if item['Name'] == "MpesaReceiptNumber"),
                            "phone_number": next(item['Value'] for item in metadata if item['Name'] == "PhoneNumber"),
                            "transaction_date": next(item['Value'] for item in metadata if item['Name'] == "TransactionDate"),
                        }
                        transaction.mpesa_receipt_number = parsed['mpesa_receipt']
                        transaction.transaction_date = parsed['transaction_date']
                    db.session.commit()
                    print("\n--- Transaction Verified as SUCCESS ---")
                    return
                elif response_data.get("ResultCode") in ["1032", "1037", "2001"]:
                    # Failed cases
                    transaction.status = "FAILED"
                    transaction.failure_reason = response_data.get("ResultDesc")
                    db.session.commit()
                    print("\n--- Transaction Verified as FAILED ---")
                    return

            except Exception as e:
                print(f"\n--- Error verifying transaction (attempt {attempt + 1}): {str(e)} ---")
                continue

        print("\n--- Max retries reached without final status ---")

@mpesa_bp.route('/callback', methods=['POST'])
def mpesa_callback():
    callback_data = request.get_json()
    transaction_ref = request.args.get('ref')

    print("\n--- FULL CALLBACK DATA RECEIVED ---")
    print(callback_data)

    if transaction_ref:
        callback_store[transaction_ref] = callback_data

    ApiLog.log("mpesa_callback_received", callback_data, {})

    return jsonify({"ResultCode": 0, "ResultDesc": "Callback received"}), 200

@mpesa_bp.route('/check_callback/<transaction_ref>', methods=['GET'])
def check_callback(transaction_ref):
    """Endpoint to check callback status (for testing)"""
    if transaction_ref in callback_store:
        return jsonify({
            "status": "received",
            "callback_data": callback_store[transaction_ref]
        })
    return jsonify({"status": "pending"}), 404