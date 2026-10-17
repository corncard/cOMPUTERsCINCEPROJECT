from pathlib import Path

import pytest

from pocketlab.analytics import category_totals, load_expenses, monthly_totals, total_spend


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "expenses.csv"


def test_load_expenses_creates_dataframe():
    df = load_expenses(DATA_PATH)
    assert not df.empty
    assert {"date", "category", "amount"}.issubset(df.columns)


def test_total_spend_matches_dataset():
    df = load_expenses(DATA_PATH)
    assert total_spend(df) == pytest.approx(2939.63, rel=1e-3)


def test_monthly_totals_and_category_totals():
    df = load_expenses(DATA_PATH)
    monthly = monthly_totals(df)
    categories = category_totals(df)

    assert monthly["total"].sum() == pytest.approx(total_spend(df), rel=1e-3)
    assert categories["total"].sum() == pytest.approx(total_spend(df), rel=1e-3)
    assert categories.iloc[0]["category"] == "Rent"
