import pytest
from self_storage import rent_due, access_allowed, payment_status

# Test cases written to execute every line of self_storage.py (line coverage).


# ---------- rent_due ----------

def test_within_deposit_months():
    assert rent_due("small", 1, False, False) == 0


def test_unknown_unit_size_raises():
    with pytest.raises(ValueError):
        rent_due("huge", 3, False, False)


def test_negative_months_raises():
    with pytest.raises(ValueError):
        rent_due("small", -1, False, False)


def test_short_stay_without_climate():
    # small covers 1 month, 2 extra months at 80
    assert rent_due("small", 3, False, False) == 160


def test_long_stay_member_with_climate():
    # member on small gets 2 months covered, 8 extra months
    # long stay discount: 120 - 10 - 5 = 105
    assert rent_due("small", 10, True, True) == 840


# ---------- access_allowed ----------

def test_access_allowed():
    assert access_allowed(12, 1, False) is True


def test_owner_access():
    assert access_allowed(3, 4, True) is True


def test_access_outside_hours():
    assert access_allowed(3, 1, False) is False


# ---------- payment_status ----------

def test_autopay_with_prior_late_current():
    assert payment_status(20, True, True) == "current"


def test_manual_pay_grace():
    assert payment_status(0, False, False) == "grace"


def test_manual_pay_lien():
    assert payment_status(-20, False, False) == "lien"
