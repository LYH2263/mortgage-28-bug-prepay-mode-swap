from pydantic import BaseModel, Field


class LoanUpdate(BaseModel):
    name: str | None = None
    principal: float | None = Field(default=None, gt=0)
    annual_rate: float | None = Field(default=None, ge=0)
    months: int | None = Field(default=None, gt=0, le=600)
