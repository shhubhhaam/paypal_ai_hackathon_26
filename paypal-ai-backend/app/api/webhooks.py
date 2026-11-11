
import json

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.paypal_service import (
    verify_webhook_signature
)
from app.services.webhook_service import (
    process_paypal_event
)


router = APIRouter(
    prefix="/webhooks",
    tags=["PayPal Webhooks"]
)

@router.post("/paypal")
async def paypal_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        raw_body = await request.body()
        event = json.loads(raw_body)

        # Preserve original body for reliable parsing
        # and do not reconstruct the event from altered fields.
        import asyncio
        raw_body = asyncio.run(request.body())

        event = json.loads(raw_body)

        headers = dict(request.headers)

        # 1. Verify webhook signature
        is_valid = verify_webhook_signature(
            headers,
            event
        )

        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="Invalid PayPal webhook signature"
            )

        # 2. Process verified event
        result = process_paypal_event(
            db,
            event
        )

        return {
            "success": True,
            **result
        }

    except HTTPException:
        raise

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Webhook processing failed"
        ) from exc
