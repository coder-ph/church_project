from routes.mpesa import mpesa_router
from flask import jsonify, request
from models.event_contribution import EventContribution
from models.transactions import Transaction
from app import db

@mpesa_router.route('/callback', methods=['POST'])
def stk_callback():
    data = request.get_json()
    
    allowed_ips = ['196.201.214.200', '196.201.214.206']  
    if request.remote_addr not in allowed_ips:
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        stk_callback = data['Body']['stkCallback']
        result_code = stk_callback['ResultCode']
        metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])

        amount = next((x['Value'] for x in metadata if x['Name'] == 'Amount'), None)
        phone = next((x['Value'] for x in metadata if x['Name'] == 'PhoneNumber'), None)
        transaction_id = stk_callback.get('MpesaReceiptNumber')
    except Exception as e:
        return jsonify({"error": "Malformed response"}), 400
    
    if Transaction.query.filter_by(transaction_id=transaction_id).first():
        return jsonify({"error": "Duplicate transaction"}), 409

    
    txn = Transaction.query.filter_by(phone=phone, status='pending').first()
    if not txn or txn.amount != amount:
        return jsonify({"error": "No matching transaction"}), 404

    
    txn.status = "success" if result_code == 0 else "failed"
    txn.transaction_id = transaction_id
    
    ec = EventContribution.query.filter_by(user_id=txn.user_id, event_id=txn.event_id).first()
    if ec:
        ec.paid_amount += amount

    db.session.commit()
    return jsonify({"result": "ok"}), 200