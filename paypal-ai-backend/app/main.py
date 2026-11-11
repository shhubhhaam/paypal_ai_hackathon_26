from fastapi import FastAPI

from app.core.database import Base, engine

# Import models before create_all
from app.models import Transaction, PaymentEvent

from app.api.webhooks import router as webhook_router


app = FastAPI(
    title="AI Payment Intelligence Engine",
    version="1.0.0"
)


# Initial development setup only.
Base.metadata.create_all(bind=engine)


app.include_router(webhook_router)


@app.get("/")
def home():

    return {
        "message": "AI Payment Intelligence API is running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }