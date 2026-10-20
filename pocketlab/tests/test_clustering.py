
import pandas as pd
import pytest

from pocketlab.ml.clustering import cluster_spending


@pytest.fixture
def sample_expenses():
    """Create sample expenses spanning six weeks."""
    return pd.DataFrame({
        "date": [
            "2026-09-01", "2026-09-03",
            "2026-09-08", "2026-09-10",
            "2026-09-15", "2026-09-17",
            "2026-09-22", "2026-09-24",
            "2026-09-29", "2026-10-01",
            "2026-10-06", "2026-10-08",
        ],
        "category": [
            "Food", "Transport",
            "Food", "Entertainment",
            "Food", "Transport",
            "Shopping", "Food",
            "Transport", "Food",
            "Shopping", "Entertainment",
        ],
        "amount": [
            30000, 10000,
            25000, 15000,
            35000, 10000,
            80000, 20000,
            12000, 30000,
            90000, 25000,
        ],
    })


def test_clustering_returns_expected_results(sample_expenses):
    profiles, model, scaler = cluster_spending(
        sample_expenses, n_clusters=3, period="W"
    )

    assert "cluster" in profiles.columns
    assert len(profiles) >= 3
    assert profiles["cluster"].nunique() == 3


def test_clustering_preserves_spending_data(sample_expenses):
    profiles, _, _ = cluster_spending(sample_expenses)

    assert "total_amount" in profiles.columns
    assert "transaction_count" in profiles.columns
    assert "average_amount" in profiles.columns
    assert (profiles["total_amount"] > 0).all()


def test_clustering_rejects_too_few_periods(sample_expenses):
    with pytest.raises(ValueError, match="Need at least"):
        cluster_spending(sample_expenses, n_clusters=10)


def test_clustering_rejects_missing_columns():
    invalid_data = pd.DataFrame({
        "date": ["2026-09-01"],
        "amount": [30000],
    })

    with pytest.raises(ValueError, match="Missing columns"):
        cluster_spending(invalid_data)
