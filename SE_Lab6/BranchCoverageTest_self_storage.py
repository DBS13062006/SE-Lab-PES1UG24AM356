import pytest
from self_storage import rent_due, access_allowed, payment_status

# Test cases written so that every decision in self_storage.py
# evaluates to both True and False (branch coverage).


# ---------- rent_due ----------

def test_within_deposit_months():
    assert rent_due("small", 1, False, False) == 0


def test_unknown_unit_size_raises():
    # unit_size not in DEPOSIT_MONTHS -> True
    with pytest.raises(ValueError):
        rent_due("huge", 3, False, False)


def test_negative_months_raises():
    # months < 0 -> True
    with pytest.raises(ValueError):
        rent_due("small", -1, False, False)


def test_zero_months():
    # boundary: months == 0 is allowed, nothing extra to pay
    assert rent_due("medium", 0, False, False) == 0


def test_extra_exactly_zero():
    # medium covers 2 months, extra == 0 -> returns 0
    assert rent_due("medium", 2, True, False) == 0


def test_member_small_gets_extra_month():
    # is_member True and not large -> covered becomes 2
    assert rent_due("small", 2, False, True) == 0
    assert rent_due("small", 3, False, True) == 80


def test_member_large_no_extra_month():
    # is_member True but unit is large -> no extra month
    # large covers 3, extra 2 at 80
    assert rent_due("large", 5, False, True) == 160


def test_short_stay_without_climate():
    # is_climate False, extra <= 6
    assert rent_due("small", 3, False, False) == 160


def test_short_stay_with_climate():
    # is_climate True, extra <= 6
    assert rent_due("small", 4, True, False) == 360


def test_extra_exactly_six_no_discount():
    # boundary: extra == 6 does not get the long stay discount
    assert rent_due("small", 7, False, False) == 480


def test_long_stay_without_climate():
    # extra > 6 and is_climate False: 80 - 10 = 70
    assert rent_due("small", 8, False, False) == 7 * 70


def test_long_stay_member_with_climate():
    # extra > 6 and is_climate True: 120 - 10 - 5 = 105
    assert rent_due("small", 10, True, True) == 840


# ---------- access_allowed ----------

def test_access_allowed():
    assert access_allowed(12, 1, False) is True


def test_owner_access_within_limit():
    assert access_allowed(3, 4, True) is True


def test_owner_access_too_many_visitors():
    assert access_allowed(12, 5, True) is False


def test_access_before_opening():
    assert access_allowed(5, 1, False) is False


def test_access_after_closing():
    assert access_allowed(23, 1, False) is False


def test_access_at_boundary_hours():
    assert access_allowed(6, 2, False) is True
    assert access_allowed(22, 2, False) is True


def test_access_too_many_visitors():
    assert access_allowed(12, 3, False) is False


# ---------- payment_status ----------

def test_autopay_current():
    # autopay, no prior late: cutoff 0
    assert payment_status(0, True, False) == "current"


def test_autopay_grace():
    assert payment_status(-1, True, False) == "grace"


def test_autopay_lien():
    assert payment_status(-16, True, False) == "lien"


def test_autopay_with_prior_late_current():
    # autopay with prior late: cutoff 10
    assert payment_status(20, True, True) == "current"


def test_manual_pay_current():
    # manual pay, no prior late: cutoff 5
    assert payment_status(5, False, False) == "current"


def test_manual_pay_grace():
    assert payment_status(0, False, False) == "grace"


def test_manual_pay_grace_lower_boundary():
    assert payment_status(-10, False, False) == "grace"


def test_manual_pay_lien():
    assert payment_status(-20, False, False) == "lien"


def test_manual_pay_with_prior_late():
    # manual pay with prior late: cutoff 15
    assert payment_status(15, False, True) == "current"
    assert payment_status(14, False, True) == "grace"
    assert payment_status(-1, False, True) == "lien"
