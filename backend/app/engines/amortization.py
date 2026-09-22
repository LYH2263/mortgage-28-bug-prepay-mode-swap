import math


def monthly_payment(principal: float, annual_rate: float, months: int) -> float:
    """等额本息月供（未四舍五入）。"""
    P = float(principal)
    n = int(months)
    r = float(annual_rate) / 12.0 / 100.0
    if n <= 0:
        raise ValueError("months")
    if r == 0:
        return P / n
    return P * r * (1 + r) ** n / ((1 + r) ** n - 1)


def equal_payment_schedule(principal: float, annual_rate: float, months: int) -> dict:
    P = float(principal)
    n = int(months)
    r = float(annual_rate) / 12.0 / 100.0
    pay = monthly_payment(P, annual_rate, n)
    rows = []
    bal = P
    interest_sum = 0.0
    for i in range(1, n + 1):
        interest = bal * r
        principal_part = pay - interest
        if i == n:
            principal_part = bal
            pay_i = principal_part + interest
        else:
            pay_i = pay
        bal = max(0.0, bal - principal_part)
        interest_sum += interest
        rows.append({
            "period": i,
            "payment": round(pay_i, 2),
            "principal": round(principal_part, 2),
            "interest": round(interest, 2),
            "balance": round(bal, 2),
        })
    return {
        "monthly_payment": round(pay if n else 0, 2),
        "total_interest": round(interest_sum, 2),
        "total_payment": round(sum(x["payment"] for x in rows), 2),
        "rows": rows,
    }


def remaining_balance(principal: float, annual_rate: float, months: int, elapsed: int) -> float:
    """等额本息第 elapsed 期期末的剩余本金（未四舍五入）。"""
    P = float(principal)
    n = int(months)
    k = int(elapsed)
    if not 0 <= k <= n:
        raise ValueError("elapsed")
    r = float(annual_rate) / 12.0 / 100.0
    pay = monthly_payment(P, annual_rate, n)
    if r == 0:
        return max(0.0, P - pay * k)
    return P * (1 + r) ** k - pay * (((1 + r) ** k - 1) / r)


def schedule_with_payment(balance: float, annual_rate: float, payment: float) -> dict:
    """以固定月供摊还指定本金，末期为残差收尾（用于缩短期限重算）。"""
    bal = float(balance)
    r = float(annual_rate) / 12.0 / 100.0
    pay = float(payment)
    if bal <= 0:
        raise ValueError("balance")
    if pay <= 0:
        raise ValueError("payment")
    if pay <= bal * r:
        raise ValueError("payment does not cover interest")
    if r == 0:
        n = math.ceil(bal / pay - 1e-9)
    else:
        n = math.ceil(math.log(pay / (pay - bal * r)) / math.log(1 + r) - 1e-9)
    rows = []
    interest_sum = 0.0
    for i in range(1, n + 1):
        interest = bal * r
        principal_part = pay - interest
        if i == n:
            principal_part = bal
            pay_i = principal_part + interest
        else:
            pay_i = pay
        bal = max(0.0, bal - principal_part)
        interest_sum += interest
        rows.append({
            "period": i,
            "payment": round(pay_i, 2),
            "principal": round(principal_part, 2),
            "interest": round(interest, 2),
            "balance": round(bal, 2),
        })
    return {
        "monthly_payment": round(pay, 2),
        "months": n,
        "total_interest": round(interest_sum, 2),
        "total_payment": round(sum(x["payment"] for x in rows), 2),
        "rows": rows,
    }
