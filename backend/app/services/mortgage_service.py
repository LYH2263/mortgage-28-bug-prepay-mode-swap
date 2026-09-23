import json

from app.db import connect
from app.engines.amortization import equal_payment_schedule
from app.modules.prepay_partial import compute_prepay
from app.repositories import loans, runs, settings

class MortgageService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_loans(self): return loans.list_all(self._c)
    def loan(self, lid): return loans.get(self._c, lid)
    def update_loan(self, lid, fields):
        if not loans.get(self._c, lid): raise LookupError("loan")
        return loans.update(self._c, lid, fields)
    def settings(self): return settings.get_map(self._c)
    def history(self, limit=50): return runs.list_recent(self._c, limit)
    def run(self, rid):
        row = runs.get(self._c, rid)
        if not row: return None
        row["input"] = json.loads(row.pop("input_json"))
        row["result"] = json.loads(row.pop("result_json"))
        return row
    def schedule(self, principal, annual_rate, months, loan_id, persist, preview_rows=12):
        full = equal_payment_schedule(principal, annual_rate, months)
        out = {k: full[k] for k in ("monthly_payment", "total_interest", "total_payment")}
        out["preview"] = full["rows"][:preview_rows]
        out["row_count"] = len(full["rows"])
        rid = None
        if persist:
            rid = runs.insert(self._c, "schedule", {"principal": principal, "annual_rate": annual_rate, "months": months}, out, loan_id)
        return {"run_id": rid, **out}
    def prepay(self, loan_id, principal, annual_rate, months, elapsed, amount, method, persist, preview_rows=12):
        if loan_id is not None:
            loan = loans.get(self._c, loan_id)
            if not loan: raise LookupError("loan")
            principal, annual_rate, months = loan["principal"], loan["annual_rate"], loan["months"]
        if principal is None or annual_rate is None or months is None:
            raise ValueError("缺少贷款要素（本金/年利率/期数）")
        out = compute_prepay(principal, annual_rate, months, elapsed, amount, method, preview_rows)
        rid = None
        if persist:
            payload = {"loan_id": loan_id, "principal": principal, "annual_rate": annual_rate,
                "months": months, "elapsed": elapsed, "amount": amount, "method": method}
            rid = runs.insert(self._c, "prepay_partial", payload, out, loan_id)
        return {"run_id": rid, **out}
    def dashboard(self):
        items = loans.list_all(self._c)
        return {"loan_count": len(items), "clean": len([x for x in items if "种子" not in x["name"]]), "dirty": len([x for x in items if "种子" in x["name"]])}


    def prepay_method_label(self, method: str) -> str:
        return method
