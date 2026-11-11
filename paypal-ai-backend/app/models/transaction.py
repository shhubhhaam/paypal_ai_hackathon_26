from sqlalchemy import (
    Column,
    String,
    Numeric,
    DateTime,
    func,
    Index
)

from app.core.database import Base


class Transaction(Base):

    __tablename__ = "transactions"

    id = Column(
        String(50),
        primary_key=True
    )

    order_id = Column(
        String(100),
        index=True,
        nullable=True
    )

    capture_id = Column(
        String(100),
        unique=True,
        nullable=False
    )

    amount = Column(
        Numeric(12, 2),
        nullable=False
    )

    currency = Column(
        String(3),
        nullable=False
    )

    status = Column(
        String(40),
        nullable=False
    )

    payment_method = Column(
        String(40),
        default="PAYPAL"
    )

    paypal_create_time = Column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )


    __table_args__ = (
        Index(
            "idx_transaction_status_created",
            "status",
            "created_at"
        ),
    )