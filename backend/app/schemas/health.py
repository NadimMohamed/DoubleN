from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Structured response body for the /health endpoint."""

    status: str = Field(..., description="Overall service status, e.g. 'ok' or 'degraded'")
    binance: str = Field(..., description="Binance connectivity status: 'connected' or 'unavailable'")
    version: str = Field(..., description="Deployed application version")
    env: str = Field(..., description="Current application environment (e.g. production, staging)")
