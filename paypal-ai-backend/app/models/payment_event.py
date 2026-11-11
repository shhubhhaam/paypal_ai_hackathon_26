from sqlalchemy import (
    Column,
    String,
    DateTime,
    JSON,
    func
)

from app.core.database import Base


class PaymentEvent(Base):

    __tablename__ = "payment_events"

    id = Column(
        String(100),
        primary_key=True
    )

    event_type = Column(
        String(100),
        nullable=False,
        index=True
    )

    resource_id = Column(
        String(100),
        nullable=True,
        index=True
    )

    resource_type = Column(
        String(50),
        nullable=True
    )

    payload = Column(
        JSON,
        nullable=False
    )

    processing_status = Column(
        String(30),
        default="RECEIVED"
    )

    paypal_create_time = Column(
        DateTime(timezone=True),
        nullable=True
    )

    received_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )