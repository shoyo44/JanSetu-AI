"""
Unit test suite for Undertrial Bail Screening Rule Engine under BNSS Section 479.
Verifies all statutory thresholds (1/3rd first-time offender, 1/2 repeat offender),
statutory exclusions (death/life imprisonment, multiple pending cases), and
judicial review categorization.
"""
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.statutory_concordance import evaluate_undertrial_relief


def test_first_time_offender_eligible():
    """Test first-time offender with 3-year offence (36 mo) detained for 13 months (>= 12 mo threshold)."""
    res = evaluate_undertrial_relief(
        offence_max_imprisonment_years=3.0,
        detention_months=13.0,
        is_first_time_offender=True,
    )
    assert res["eligible_for_review"] is True
    assert res["threshold_fraction"] == "one-third (1/3rd)"
    assert res["threshold_months"] == 12.0
    assert "BNSS §479 (First Proviso)" in res["statutory_basis"]
    assert "judicial_discretion_caveat" in res


def test_first_time_offender_not_yet_eligible():
    """Test first-time offender with 3-year offence (36 mo) detained for 8 months (< 12 mo threshold)."""
    res = evaluate_undertrial_relief(
        offence_max_imprisonment_years=3.0,
        detention_months=8.0,
        is_first_time_offender=True,
    )
    assert res["eligible_for_review"] is False
    assert res["threshold_months"] == 12.0
    assert "Shortfall: 4.0 months" in res["reason"]


def test_repeat_offender_half_sentence_rule():
    """Test non-first-time offender with 7-year offence (84 mo): needs 42 months (1/2)."""
    # 40 months -> Not eligible
    res_under = evaluate_undertrial_relief(
        offence_max_imprisonment_years=7.0,
        detention_months=40.0,
        is_first_time_offender=False,
    )
    assert res_under["eligible_for_review"] is False
    assert res_under["threshold_fraction"] == "one-half (1/2)"
    assert res_under["threshold_months"] == 42.0

    # 43 months -> Eligible
    res_over = evaluate_undertrial_relief(
        offence_max_imprisonment_years=7.0,
        detention_months=43.0,
        is_first_time_offender=False,
    )
    assert res_over["eligible_for_review"] is True


def test_exclusion_death_or_life_imprisonment():
    """Test statutory exclusion: offences punishable by death or life imprisonment are excluded."""
    res = evaluate_undertrial_relief(
        offence_max_imprisonment_years=10.0,
        detention_months=60.0,
        is_first_time_offender=True,
        is_death_or_life_offence=True,
    )
    assert res["eligible_for_review"] is False
    assert "death_or_life_imprisonment_exclusion" in res["exclusions_triggered"]
    assert "Second Proviso" in res["statutory_basis"]


def test_exclusion_multiple_pending_cases():
    """Test statutory exclusion: multiple pending cases bar relief under Section 479 third proviso."""
    res = evaluate_undertrial_relief(
        offence_max_imprisonment_years=5.0,
        detention_months=30.0,
        is_first_time_offender=True,
        has_multiple_pending_cases=True,
    )
    assert res["eligible_for_review"] is False
    assert "multiple_pending_cases_exclusion" in res["exclusions_triggered"]
    assert "Third Proviso" in res["statutory_basis"]


if __name__ == "__main__":
    test_first_time_offender_eligible()
    test_first_time_offender_not_yet_eligible()
    test_repeat_offender_half_sentence_rule()
    test_exclusion_death_or_life_imprisonment()
    test_exclusion_multiple_pending_cases()
    print("All 5 BNSS §479 Undertrial Rule Tests Passed (100.0%)!")
