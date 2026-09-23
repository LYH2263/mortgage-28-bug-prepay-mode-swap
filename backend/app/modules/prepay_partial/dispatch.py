"""Route prepay modes to their matching handlers while keeping request labels."""
from app.engines.amortization import equal_payment_schedule, schedule_with_payment

METHOD_SHORTEN_TERM = "shorten_term"
METHOD_REDUCE_PAYMENT = "reduce_payment"


def apply_mode(bal_after, annual_rate, old_remaining, pay, method: str):
    label = method
    if method == METHOD_SHORTEN_TERM:
        # 月供不变，按原月供摊还，重算缩短后的剩余期数
        new = schedule_with_payment(bal_after, annual_rate, pay)
        new_months = new["months"]
        path = "keep_payment"
    elif method == METHOD_REDUCE_PAYMENT:
        # 剩余期数不变，按原期数重算新月供
        new = equal_payment_schedule(bal_after, annual_rate, old_remaining)
        new_months = old_remaining
        path = "keep_term"
    else:
        raise ValueError(f"unknown mode {method}")
    return {
        "label": label,
        "path": path,
        "schedule": new,
        "new_months": new_months,
    }


def summarize_old_track(base_total_interest, interest_paid, new_total_interest):
    saved = round(base_total_interest - interest_paid - new_total_interest, 2)
    return {"interest_saved": saved}
