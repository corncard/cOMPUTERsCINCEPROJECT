from pathlib import Path

import pytest

from pocketlab.analytics import load_expenses
from pocketlab.insights import compute_insights


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "expenses.csv"


def test_compute_insights_returns_expected_keys():
    expenses = load_expenses(DATA_PATH)
    result = compute_insights(expenses, budget=3500)

    assert "summary" in result
    assert "category_breakdown" in result
    assert "monthly_totals" in result
    assert "narrative" in result
    assert result["summary"]["top_category"] == "Rent"
    assert result["latest_month_spend"] == pytest.approx(313.25)
    assert result["previous_month_spend"] == pytest.approx(438.90)
    assert result["monthly_change"] == pytest.approx(-125.65)
    assert result["budget_used_pct"] == pytest.approx(8.95)
    assert any("down" in item for item in result["narrative"])


def test_compute_insights_accepts_path_without_budget():
    result = compute_insights(DATA_PATH)
    assert result["budget_used_pct"] is None
    assert len(result["category_breakdown"]) == 5


def test_compute_insights_reports_unchanged_spend():
    result = compute_insights(
        [
            {"date": "2024-01-01", "category": "Food", "amount": 25},
            {"date": "2024-02-01", "category": "Food", "amount": 25},
        ]
    )
    assert result["monthly_change"] == pytest.approx(0)
    assert any("unchanged" in item for item in result["narrative"])
