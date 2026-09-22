from fastapi import APIRouter, HTTPException
from app.schemas.loans import LoanUpdate
from app.services.mortgage_service import MortgageService
router = APIRouter()
@router.get("/loans")
def list_loans():
    with MortgageService() as s: return {"items": s.list_loans()}
@router.get("/loans/{loan_id}")
def get_loan(loan_id: int):
    with MortgageService() as s:
        row = s.loan(loan_id)
        if not row: raise HTTPException(404)
        return row
@router.patch("/loans/{loan_id}")
def patch_loan(loan_id: int, body: LoanUpdate):
    with MortgageService() as s:
        try:
            return s.update_loan(loan_id, body.model_dump(exclude_unset=True))
        except LookupError:
            raise HTTPException(404)
