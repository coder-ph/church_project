import os, requests
from requests.auth import HTTPBasicAuth

def get_mpesa_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" \
        if os.getenv("MPESA_ENV") == "sandbox" else \
        "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    response = requests.get(url, auth=HTTPBasicAuth(
        os.getenv('MPESA_CONSUMER_KEY'),
        os.getenv('MPESA_CONSUMER_SECRET')
    ))
    
    response.raise_for_status()
    return response.json()['access_token']