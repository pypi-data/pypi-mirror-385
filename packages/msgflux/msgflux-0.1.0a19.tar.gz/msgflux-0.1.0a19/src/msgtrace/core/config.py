"""Configuration for msgtrace."""

from typing import List

from pydantic import BaseModel, Field


class MsgTraceConfig(BaseModel):
    """Configuration for msgtrace server."""

    # Server configuration
    host: str = Field(default="0.0.0.0", description="Host to bind the server to")
    port: int = Field(default=4321, description="Port to bind the server to")

    # Database configuration
    db_path: str = Field(default="msgtrace.db", description="Path to SQLite database")

    # CORS configuration
    cors_origins: List[str] = Field(
        default=["*"], description="Allowed CORS origins"
    )

    # Collector configuration
    queue_size: int = Field(
        default=1000, description="Maximum size of processing queue"
    )

    class Config:
        arbitrary_types_allowed = True
