from pydantic import BaseModel, Field


class Polling(BaseModel):
    max_retries: int = Field(default=100, ge=1)
    poll_interval: float = Field(default=1.0, gt=0)
    backoff_factor: float = Field(default=2.0, gt=0)
    max_poll_interval: float | None = Field(default=20.0, gt=0)
    jitter: float | None = Field(default=0.25, gt=0)
