
import requests

from app.core.config import settings


def get_access_token():

    response = requests.post(
        f"{settings.PAYPAL_BASE_URL}/v1/oauth2/token",
        auth=(
            settings.PAYPAL_CLIENT_ID,
            settings.PAYPAL_CLIENT_SECRET
        ),
        data={
            "grant_type": "client_credentials"
        },
        headers={
            "Accept": "application/json"
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()["access_token"]


def verify_webhook_signature(
    headers: dict,
    webhook_event: dict
):

    token = get_access_token()

    payload = {
        "auth_algo": headers.get("paypal-auth-algo"),
        "cert_url": headers.get("paypal-cert-url"),
        "transmission_id": headers.get(
            "paypal-transmission-id"
        ),
        "transmission_sig": headers.get(
            "paypal-transmission-sig"
        ),
        "transmission_time": headers.get(
            "paypal-transmission-time"
        ),
        "webhook_id": settings.PAYPAL_WEBHOOK_ID,
        "webhook_event": webhook_event
    }

    required_fields = [
        "auth_algo",
        "cert_url",
        "transmission_id",
        "transmission_sig",
        "transmission_time"
    ]

    if any(not payload.get(field) for field in required_fields):
        raise ValueError("Missing PayPal signature headers")

    response = requests.post(
        (
            f"{settings.PAYPAL_BASE_URL}"
            "/v1/notifications/verify-webhook-signature"
        ),
        json=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    return result.get("verification_status") == "SUCCESS"
