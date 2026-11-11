
import os
import requests
from dotenv import load_dotenv

load_dotenv()

PAYPAL_BASE_URL = os.getenv("PAYPAL_BASE_URL")
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
PAYPAL_WEBHOOK_ID = os.getenv("PAYPAL_WEBHOOK_ID")


def get_access_token():
    response = requests.post(
        f"{PAYPAL_BASE_URL}/v1/oauth2/token",
        auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
        data={"grant_type": "client_credentials"},
        headers={"Accept": "application/json"},
        timeout=30
    )
    response.raise_for_status()
    return response.json()["access_token"]


def verify_webhook_signature(headers, webhook_event):
    access_token = get_access_token()

    payload = {
        "auth_algo": headers.get("paypal-auth-algo"),
        "cert_url": headers.get("paypal-cert-url"),
        "transmission_id": headers.get("paypal-transmission-id"),
        "transmission_sig": headers.get("paypal-transmission-sig"),
        "transmission_time": headers.get("paypal-transmission-time"),
        "webhook_id": PAYPAL_WEBHOOK_ID,
        "webhook_event": webhook_event
    }

    response = requests.post(
        f"{PAYPAL_BASE_URL}/v1/notifications/verify-webhook-signature",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        },
        json=payload,
        timeout=30
    )

    response.raise_for_status()

    return response.json().get("verification_status") == "SUCCESS"
