from fastapi import APIRouter, HTTPException
from app.schemas.prepay import PrepayRequest
from app.services.mortgage_service import MortgageService

router = APIRouter()

@router.post("/prepay")
def post_prepay(body: PrepayRequest):
    with MortgageService() as s:
        try:
            out = s.prepay(body.loan_id, body.principal, body.annual_rate, body.months,
                body.elapsed, body.amount, body.method, body.persist, body.preview_rows)
            out["method"] = s.prepay_method_label(body.method)
            return out
        except LookupError:
            raise HTTPException(404, "贷款不存在")
        except ValueError as e:
            raise HTTPException(400, str(e))
