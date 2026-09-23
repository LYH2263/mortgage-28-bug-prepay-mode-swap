"""提前还部分本金：等额本息贷款在已还若干期后提前偿还部分本金。

处理方式：
- shorten_term   保持原月供不变，重算剩余期数；
- reduce_payment 保持剩余期数不变，重算新月供。

入参校验失败（已过期数越界、金额非正或不严格小于当期期末剩余本金、
处理方式未知）一律抛 ValueError，由上层拒绝请求且不落库。
"""

from app.engines.amortization import (
    equal_payment_schedule,
    monthly_payment,
    remaining_balance,
)
from app.modules.prepay_partial.dispatch import apply_mode, summarize_old_track

METHOD_SHORTEN_TERM = "shorten_term"
METHOD_REDUCE_PAYMENT = "reduce_payment"
METHODS = (METHOD_SHORTEN_TERM, METHOD_REDUCE_PAYMENT)


def compute_prepay(
    principal: float,
    annual_rate: float,
    months: int,
    elapsed: int,
    amount: float,
    method: str,
    preview_rows: int = 12,
) -> dict:
    if method not in METHODS:
        raise ValueError(f"未知处理方式: {method}")
    n = int(months)
    k = int(elapsed)
    if k < 1 or k > n - 1:
        raise ValueError(f"已过期数须落在 1 到 {n - 1} 之间")
    amount = float(amount)
    if amount <= 0:
        raise ValueError("提前还金额须为正")

    pay = monthly_payment(principal, annual_rate, n)
    base = equal_payment_schedule(principal, annual_rate, n)
    bal_before = remaining_balance(principal, annual_rate, n, k)
    if amount >= bal_before:
        raise ValueError("提前还金额须严格小于该期期末剩余本金")

    bal_after = bal_before - amount
    old_remaining = n - k
    routed = apply_mode(bal_after, annual_rate, old_remaining, pay, method)
    new = routed["schedule"]
    new_months = routed["new_months"]

    interest_paid = k * pay - (float(principal) - bal_before)
    extra = summarize_old_track(base["total_interest"], interest_paid, new["total_interest"])
    return {
        "method": routed["label"],
        "elapsed": k,
        "amount": round(amount, 2),
        "balance_before": round(bal_before, 2),
        "balance_after": round(bal_after, 2),
        "old_monthly_payment": round(pay, 2),
        "new_monthly_payment": new["monthly_payment"],
        "old_remaining_months": old_remaining,
        "new_remaining_months": new_months,
        "interest_paid": round(interest_paid, 2),
        "total_interest": new["total_interest"],
        "interest_saved": extra["interest_saved"],
        "preview": new["rows"][:preview_rows],
        "row_count": len(new["rows"]),
    }
