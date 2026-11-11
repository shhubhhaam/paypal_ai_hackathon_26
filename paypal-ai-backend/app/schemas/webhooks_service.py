
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.payment_event import PaymentEvent


CAPTURE_EVENT_STATUS = {
    "PAYMENT.CAPTURE.PENDING": "PENDING",
    "PAYMENT.CAPTURE.COMPLETED": "COMPLETED",
    "PAYMENT.CAPTURE.DENIED": "DENIED",
    "PAYMENT.CAPTURE.REVERSED": "REVERSED"
}


def parse_datetime(value):

    if not value:
        return None

    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )


def process_paypal_event(
    db: Session,
    event: dict
):

    event_id = event.get("id")
    event_type = event.get("event_type")
    resource = event.get("resource", {})

    if not event_id or not event_type:
        raise ValueError("Invalid PayPal event")

    # 1. Idempotency check
    existing = db.get(PaymentEvent, event_id)

    if existing:
        return {
            "message": "Event already processed",
            "duplicate": True
        }

    # 2. Save original event
    payment_event = PaymentEvent(
        id=event_id,
        event_type=event_type,
        resource_id=resource.get("id"),
        resource_type=event.get("resource_type"),
        payload=event,
        processing_status="RECEIVED",
        paypal_create_time=parse_datetime(
            event.get("create_time")
        )
    )

    db.add(payment_event)

    # 3. Process supported capture events
    new_status = CAPTURE_EVENT_STATUS.get(event_type)

    if new_status:

        capture_id = resource.get("id")

        if not capture_id:
            raise ValueError("Capture ID missing")

        amount_data = resource.get("amount", {})

        amount = amount_data.get("value")
        currency = amount_data.get("currency_code")

        if amount is None or not currency:
            raise ValueError("Capture amount missing")

        order_id = (
            resource.get("supplementary_data", {})
            .get("related_ids", {})
            .get("order_id")
        )

        # 4. Find existing transaction
        transaction = db.execute(
            select(Transaction).where(
                Transaction.capture_id == capture_id
            )
        ).scalar_one_or_none()

        if transaction is None:

            transaction = Transaction(
                id=capture_id,
                capture_id=capture_id,
                order_id=order_id,
                amount=Decimal(str(amount)),
                currency=currency,
                status=new_status
            )

            db.add(transaction)

        else:

            # Avoid regressing a completed capture
            if transaction.status != "COMPLETED":
                transaction.status = new_status

            if order_id:
                transaction.order_id = order_id

        payment_event.processing_status = "PROCESSED"

    else:
        # Preserve events that we have not normalized yet.
        payment_event.processing_status = "STORED"

    # 5. Commit event and transaction together
    db.commit()

    return {
        "message": "PayPal event processed",
        "event_id": event_id,
        "event_type": event_type,
        "duplicate": False
    }
