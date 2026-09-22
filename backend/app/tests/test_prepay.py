import pytest

from app.engines.amortization import (
    equal_payment_schedule,
    remaining_balance,
    schedule_with_payment,
)
from app.modules.prepay_partial import compute_prepay

P, RATE, N = 1_000_000, 3.5, 360


def test_remaining_balance_matches_schedule_rows():
    sch = equal_payment_schedule(P, RATE, N)
    for k in (1, 12, 120, 359):
        assert remaining_balance(P, RATE, N, k) == pytest.approx(sch["rows"][k - 1]["balance"], abs=0.01)
    assert remaining_balance(P, RATE, N, 0) == pytest.approx(P)
    assert remaining_balance(P, RATE, N, N) == pytest.approx(0, abs=0.01)


def test_elapsed_out_of_range_rejected():
    for bad in (0, -1, N, N + 5):
        with pytest.raises(ValueError):
            compute_prepay(P, RATE, N, bad, 100_000, "reduce_payment")


def test_elapsed_boundary_ok():
    out = compute_prepay(P, RATE, N, N - 1, 1_000, "reduce_payment")
    assert out["elapsed"] == N - 1
    assert out["old_remaining_months"] == 1


def test_amount_must_be_positive():
    for bad in (0, -10):
        with pytest.raises(ValueError):
            compute_prepay(P, RATE, N, 12, bad, "shorten_term")


def test_amount_must_be_strictly_below_balance():
    bal = remaining_balance(P, RATE, N, 12)
    with pytest.raises(ValueError):
        compute_prepay(P, RATE, N, 12, bal, "shorten_term")
    with pytest.raises(ValueError):
        compute_prepay(P, RATE, N, 12, bal + 1, "reduce_payment")
    out = compute_prepay(P, RATE, N, 12, bal - 0.01, "reduce_payment")
    assert out["balance_after"] == pytest.approx(0.01, abs=1e-9)


def test_unknown_method_rejected():
    with pytest.raises(ValueError):
        compute_prepay(P, RATE, N, 12, 10_000, "write_off")


def test_reduce_payment_keeps_term_lowers_payment():
    out = compute_prepay(P, RATE, N, 12, 100_000, "reduce_payment")
    assert out["method"] == "reduce_payment"
    assert out["balance_before"] == pytest.approx(remaining_balance(P, RATE, N, 12), abs=0.01)
    assert out["balance_after"] == pytest.approx(out["balance_before"] - 100_000, abs=0.01)
    assert out["new_remaining_months"] == out["old_remaining_months"] == N - 12
    assert 0 < out["new_monthly_payment"] < out["old_monthly_payment"]
    expect = equal_payment_schedule(out["balance_after"], RATE, N - 12)
    assert out["new_monthly_payment"] == expect["monthly_payment"]
    assert out["total_interest"] == expect["total_interest"]
    assert out["interest_saved"] > 0
    assert out["row_count"] == N - 12
    assert len(out["preview"]) == 12


def test_shorten_term_keeps_payment_shortens_term():
    out = compute_prepay(P, RATE, N, 12, 100_000, "shorten_term")
    assert out["method"] == "shorten_term"
    assert out["new_monthly_payment"] == out["old_monthly_payment"]
    assert 0 < out["new_remaining_months"] < out["old_remaining_months"]
    assert out["row_count"] == out["new_remaining_months"]
    assert out["interest_saved"] > 0
    last = out["preview"][-1] if out["row_count"] <= 12 else None
    if last:
        assert last["balance"] == 0


def test_methods_differ_on_same_inputs():
    a = compute_prepay(P, RATE, N, 12, 100_000, "shorten_term")
    b = compute_prepay(P, RATE, N, 12, 100_000, "reduce_payment")
    assert a["balance_before"] == b["balance_before"]
    assert a["balance_after"] == b["balance_after"]
    assert a["new_remaining_months"] != b["new_remaining_months"]
    assert a["new_monthly_payment"] != b["new_monthly_payment"]


def test_schedule_with_payment_zero_rate():
    s = schedule_with_payment(10_000, 0, 1_000)
    assert s["months"] == 10
    assert s["total_interest"] == 0
    assert s["rows"][-1]["balance"] == 0


def test_schedule_with_payment_residual_last_row():
    s = schedule_with_payment(100_000, 6.0, 2_000)
    assert s["rows"][-1]["balance"] == 0
    assert s["rows"][-1]["payment"] < 2_000
    assert all(r["payment"] == 2_000 for r in s["rows"][:-1])


def test_schedule_with_payment_rejects_bad_input():
    with pytest.raises(ValueError):
        schedule_with_payment(0, 3.5, 1_000)
    with pytest.raises(ValueError):
        schedule_with_payment(100_000, 3.5, 100)  # 月供不足以覆盖利息
