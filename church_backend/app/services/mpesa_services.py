import os, requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
load_dotenv()

def get_mpesa_token():
    print(" CONSUMER KEY:", os.getenv('MPESA_CONSUMER_KEY'))
    print(" CONSUMER SECRET:", os.getenv('MPESA_CONSUMER_SECRET'))
    print(" ENV:", os.getenv('MPESA_ENV'))

    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" \
        if os.getenv("MPESA_ENV") == "sandbox" else \
        "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    response = requests.get(url, auth=HTTPBasicAuth(
        os.getenv('MPESA_CONSUMER_KEY'),
        os.getenv('MPESA_CONSUMER_SECRET')
    ))

    print(" Raw response:", response.text)
    
    response.raise_for_status()
    return {
        'access_token': response.json()['access_token'],
        'expires_in': response.json().get('expires_in', 3599)
    }