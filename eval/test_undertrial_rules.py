"""
Unit test suite for Undertrial Bail Screening Rule Engine under BNSS Section 479.
Verifies all statutory thresholds (1/3rd first-time offender on bond, 1/2 repeat offender),
statutory exclusions (death/life imprisonment, multiple pending cases),
delay caused by the accused (excluded under Explanation to §479(1)),
full-maximum-period statutory detention ceiling,
judicial order for continued detention with written reasons,
and jail superintendent application duty under §479(3).
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
    assert "BNSS §479(1) (First Proviso - First-Time Offender)" in res["statutory_basis"]
    assert res["jail_superintendent_duty_triggered"] is True
    assert "bond" in res["reason"]
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
    assert res["jail_superintendent_duty_triggered"] is False


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
    assert res_over["jail_superintendent_duty_triggered"] is True


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
    assert "Capital / Life Imprisonment" in res["statutory_basis"]


def test_exclusion_multiple_pending_cases():
    """Test statutory exclusion: multiple pending cases bar relief under Section 479(2)."""
    res = evaluate_undertrial_relief(
        offence_max_imprisonment_years=5.0,
        detention_months=30.0,
        is_first_time_offender=True,
        has_multiple_pending_cases=True,
    )
    assert res["eligible_for_review"] is False
    assert "multiple_pending_cases_exclusion" in res["exclusions_triggered"]
    assert "BNSS §479(2)" in res["statutory_basis"]


def test_delay_caused_by_accused_excluded():
    """Test Explanation to §479(1): delay caused by accused is subtracted from effective detention."""
    # 3-year offence (36 mo), threshold is 12 mo (1/3).
    # Gross detention is 14 months, but 4 months delay was caused by accused.
    # Effective detention = 10 months (< 12 mo threshold) -> NOT ELIGIBLE.
    res = evaluate_undertrial_relief(
        offence_max_imprisonment_years=3.0,
        detention_months=14.0,
        is_first_time_offender=True,
        delay_caused_by_accused_months=4.0,
    )
    assert res["eligible_for_review"] is False
    assert res["effective_detention_months"] == 10.0
    assert res["delay_excluded_months"] == 4.0
    assert "Shortfall: 2.0 months" in res["reason"]


def test_full_maximum_period_ceiling():
    """Test proviso to §479(1): detention cannot exceed maximum period of imprisonment under any circumstances."""
    # 3-year offence (36 mo max). Accused has undergone 37 months detention.
    res = evaluate_undertrial_relief(
        offence_max_imprisonment_years=3.0,
        detention_months=37.0,
        is_first_time_offender=False,
    )
    assert res["eligible_for_review"] is True
    assert res["threshold_fraction"] == "full-maximum (100%)"
    assert "Maximum Period Detention Bar" in res["statutory_basis"]
    assert res["jail_superintendent_duty_triggered"] is True


def test_court_ordered_continued_detention():
    """Test second proviso to §479(1): court may order continued detention for reasons in writing."""
    # Accused meets 1/2 threshold, but court issued an order for continued detention after hearing prosecutor
    res = evaluate_undertrial_relief(
        offence_max_imprisonment_years=6.0,
        detention_months=40.0,
        is_first_time_offender=False,
        court_ordered_continued_detention=True,
        court_order_reasons="Flight risk and witness intimidation corroborated by prosecution evidence",
    )
    assert res["eligible_for_review"] is False
    assert "judicial_continuation_order" in res["exclusions_triggered"]
    assert "Flight risk" in res["reason"]


if __name__ == "__main__":
    test_first_time_offender_eligible()
    test_first_time_offender_not_yet_eligible()
    test_repeat_offender_half_sentence_rule()
    test_exclusion_death_or_life_imprisonment()
    test_exclusion_multiple_pending_cases()
    test_delay_caused_by_accused_excluded()
    test_full_maximum_period_ceiling()
    test_court_ordered_continued_detention()
    print("All 8 BNSS §479 Undertrial Rule Tests Passed (100.0%)!")
