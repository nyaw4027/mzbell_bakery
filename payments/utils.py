import requests
import uuid
from django.conf import settings

BASE_URL = "https://sandbox.momodeveloper.mtn.com"

def get_token():
    url = f"{BASE_URL}/collection/token/"
    headers = {
        "Ocp-Apim-Subscription-Key": settings.MTN_MOMO_SUBSCRIPTION_KEY,
        "Authorization": f"Basic {settings.MTN_MOMO_AUTH_BASIC}"  # base64 encoded "user:pass"
    }
    response = requests.post(url, headers=headers)
    return response.json().get('access_token')

def initiate_collection_request(amount, phone, external_id, currency="GHS"):
    url = f"{BASE_URL}/collection/v1_0/requesttopay"
    headers = {
        "Authorization": f"Bearer {get_token()}",
        "X-Reference-Id": str(uuid.uuid4()),
        "X-Target-Environment": settings.MTN_MOMO_ENVIRONMENT,
        "Ocp-Apim-Subscription-Key": settings.MTN_MOMO_SUBSCRIPTION_KEY,
        "Content-Type": "application/json",
    }
    data = {
        "amount": str(amount),
        "currency": currency,
        "externalId": str(external_id),
        "payer": {
            "partyIdType": "MSISDN",
            "partyId": phone
        },
        "payerMessage": "MzBell Bakery Payment",
        "payeeNote": "Order Payment"
    }
    response = requests.post(url, json=data, headers=headers)
    return response.status_code, headers['X-Reference-Id']
