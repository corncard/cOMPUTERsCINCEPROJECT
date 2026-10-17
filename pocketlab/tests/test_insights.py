from pocketlab.analytics import load_expenses
from pocketlab.insights import compute_insights


def test_compute_insights_returns_expected_keys():
    expenses = load_expenses("data/raw/expenses.csv")
    result = compute_insights(expenses, budget=3500)

    assert "summary" in result
    assert "category_breakdown" in result
    assert "monthly_totals" in result
    assert "narrative" in result
    assert result["budget_used_pct"] is not None
