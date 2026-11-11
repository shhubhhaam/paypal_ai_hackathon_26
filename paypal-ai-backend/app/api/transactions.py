from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.transaction import Transaction
from app.models.payment_event import PaymentEvent


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


@router.get("/")
def get_transactions(
    db: Session = Depends(get_db)
):

    transactions = (
        db.query(Transaction)
        .order_by(Transaction.created_at.desc())
        .limit(100)
        .all()
    )

    return [
        {
            "id": t.id,
            "order_id": t.order_id,
            "capture_id": t.capture_id,
            "amount": float(t.amount),
            "currency": t.currency,
            "status": t.status,
            "created_at": t.created_at
        }
        for t in transactions
    ]


@router.get("/stats")
def get_transaction_stats(
    db: Session = Depends(get_db)
):

    transactions = db.query(Transaction).all()

    total = len(transactions)

    completed = sum(
        1 for t in transactions
        if t.status == "COMPLETED"
    )

    pending = sum(
        1 for t in transactions
        if t.status == "PENDING"
    )

    denied = sum(
        1 for t in transactions
        if t.status == "DENIED"
    )

    return {
        "total_transactions": total,
        "completed": completed,
        "pending": pending,
        "denied": denied,
        "success_rate": (
            round(completed / total * 100, 2)
            if total else 0
        )
    }


@router.get("/events")
def get_payment_events(
    db: Session = Depends(get_db)
):

    events = (
        db.query(PaymentEvent)
        .order_by(PaymentEvent.received_at.desc())
        .limit(100)
        .all()
    )

    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "resource_id": e.resource_id,
            "processing_status": e.processing_status,
            "received_at": e.received_at
        }
        for e in events
    ]