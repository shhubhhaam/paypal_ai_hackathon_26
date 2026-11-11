
import json
import traceback

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.paypal_service import verify_webhook_signature
from app.services.webhook_service import process_paypal_event


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
        # 1. Read request body exactly once
        raw_body = await request.body()

        # 2. Parse JSON
        event = json.loads(raw_body)

        # 3. Extract PayPal headers
        headers = dict(request.headers)

        # 4. Verify PayPal webhook signature
        is_valid = verify_webhook_signature(
            headers,
            event
        )

        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="Invalid PayPal webhook signature"
            )

        # 5. Process verified event
        result = process_paypal_event(
            db,
            event
        )

        return {
            "success": True,
            **result
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()

        print("WEBHOOK PROCESSING ERROR:", repr(e))
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="Webhook processing failed"
        ) from e
