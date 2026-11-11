
import os
import requests

from dotenv import load_dotenv

load_dotenv()


# --------------------------------------------------
# PayPal Configuration
# --------------------------------------------------

PAYPAL_BASE_URL = os.getenv(
    "PAYPAL_BASE_URL",
    "https://api-m.sandbox.paypal.com"
).rstrip("/")

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
PAYPAL_WEBHOOK_ID = os.getenv("PAYPAL_WEBHOOK_ID")


# --------------------------------------------------
# Validate Configuration
# --------------------------------------------------

def validate_paypal_config():
    required = {
        "PAYPAL_CLIENT_ID": PAYPAL_CLIENT_ID,
        "PAYPAL_CLIENT_SECRET": PAYPAL_CLIENT_SECRET,
        "PAYPAL_WEBHOOK_ID": PAYPAL_WEBHOOK_ID,
        "PAYPAL_BASE_URL": PAYPAL_BASE_URL
    }

    missing = [
        key for key, value in required.items()
        if not value
    ]

    if missing:
        raise ValueError(
            f"Missing PayPal configuration: {', '.join(missing)}"
        )


# --------------------------------------------------
# Get PayPal OAuth Access Token
# --------------------------------------------------

def get_access_token():

    validate_paypal_config()

    url = f"{PAYPAL_BASE_URL}/v1/oauth2/token"

    try:
        response = requests.post(
            url,
            auth=(
                PAYPAL_CLIENT_ID,
                PAYPAL_CLIENT_SECRET
            ),
            data={
                "grant_type": "client_credentials"
            },
            headers={
                "Accept": "application/json",
                "Accept-Language": "en_US"
            },
            timeout=30
        )

        if not response.ok:
            print("PayPal OAuth Error:", response.status_code)
            print("PayPal Response:", response.text)

            response.raise_for_status()

        token_data = response.json()

        access_token = token_data.get("access_token")

        if not access_token:
            raise RuntimeError(
                "PayPal did not return an access token"
            )

        return access_token

    except requests.RequestException as e:
        print("PayPal OAuth Connection Error:", repr(e))
        raise


# --------------------------------------------------
# Verify PayPal Webhook Signature
# --------------------------------------------------

def verify_webhook_signature(headers, webhook_event):

    validate_paypal_config()

    # Required PayPal transmission headers
    required_headers = [
        "paypal-auth-algo",
        "paypal-cert-url",
        "paypal-transmission-id",
        "paypal-transmission-sig",
        "paypal-transmission-time"
    ]

    # Normalize header names
    normalized_headers = {
        key.lower(): value
        for key, value in headers.items()
    }

    # Check missing headers
    missing_headers = [
        header
        for header in required_headers
        if not normalized_headers.get(header)
    ]

    if missing_headers:
        print("Missing PayPal headers:", missing_headers)
        return False

    # Obtain OAuth access token
    access_token = get_access_token()

    # Build verification payload
    payload = {
        "auth_algo": normalized_headers["paypal-auth-algo"],
        "cert_url": normalized_headers["paypal-cert-url"],
        "transmission_id": normalized_headers["paypal-transmission-id"],
        "transmission_sig": normalized_headers["paypal-transmission-sig"],
        "transmission_time": normalized_headers["paypal-transmission-time"],
        "webhook_id": PAYPAL_WEBHOOK_ID,
        "webhook_event": webhook_event
    }

    verification_url = (
        f"{PAYPAL_BASE_URL}/v1/notifications/verify-webhook-signature"
    )

    try:
        response = requests.post(
            verification_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            },
            json=payload,
            timeout=30
        )

        # Handle PayPal API errors
        if not response.ok:

            print("\n--- PayPal Webhook Verification Error ---")
            print("HTTP Status:", response.status_code)
            print("Response:", response.text)
            print("-----------------------------------------\n")

            response.raise_for_status()

        result = response.json()

        verification_status = result.get(
            "verification_status"
        )

        print("Webhook Verification Status:", verification_status)

        return verification_status == "SUCCESS"

    except requests.RequestException as e:

        print("Webhook Verification Request Failed:", repr(e))
        raise
