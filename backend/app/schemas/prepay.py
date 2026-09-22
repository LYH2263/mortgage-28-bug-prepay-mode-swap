from typing import Literal

from pydantic import BaseModel, Field


class PrepayRequest(BaseModel):
    loan_id: int | None = None
    principal: float | None = Field(default=None, gt=0)
    annual_rate: float | None = Field(default=None, ge=0)
    months: int | None = Field(default=None, gt=0, le=600)
    elapsed: int = Field(ge=1)
    amount: float = Field(gt=0)
    method: Literal["shorten_term", "reduce_payment"]
    persist: bool = True
    preview_rows: int = Field(default=12, ge=1, le=120)
