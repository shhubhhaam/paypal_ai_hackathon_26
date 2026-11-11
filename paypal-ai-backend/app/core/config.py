from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    DATABASE_URL: str

    PAYPAL_CLIENT_ID: str
    PAYPAL_CLIENT_SECRET: str

    PAYPAL_BASE_URL: str = (
        "https://api-m.sandbox.paypal.com"
    )

    PAYPAL_WEBHOOK_ID: str

    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()