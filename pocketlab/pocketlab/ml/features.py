"""Feature engineering for PocketLab spending data."""

import pandas as pd


def build_spending_profiles(df, period="W"):
    """Convert transactions into weekly or monthly spending profiles.

    Each row represents a calendar week or month. Periods without transactions
    remain in the result with zero-valued spending features.
    """
    required_columns = {"date", "category", "amount"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    if period not in {"W", "M"}:
        raise ValueError("period must be 'W' for weekly or 'M' for monthly profiles.")

    transactions = df.loc[:, ["date", "category", "amount"]].copy()
    transactions["date"] = pd.to_datetime(transactions["date"], errors="coerce")
    transactions["amount"] = pd.to_numeric(
        transactions["amount"], errors="coerce"
    )
    transactions = transactions.dropna(subset=["date", "amount"])
    transactions = transactions.loc[transactions["amount"] > 0].copy()
    transactions["category"] = transactions["category"].fillna("Other").astype(str)

    if transactions.empty:
        raise ValueError("No valid expense transactions found.")

    # Use explicit calendar period ends while preserving the public W/M options.
    resample_frequency = "W-SUN" if period == "W" else "ME"
    indexed_transactions = transactions.set_index("date")

    total_amount = indexed_transactions["amount"].resample(resample_frequency).sum()
    transaction_count = (
        indexed_transactions["amount"].resample(resample_frequency).count()
    )
    average_amount = total_amount.div(transaction_count.where(transaction_count > 0))

    category_amounts = (
        indexed_transactions.groupby(
            [pd.Grouper(freq=resample_frequency), "category"]
        )["amount"]
        .sum()
        .unstack(fill_value=0)
        .reindex(total_amount.index, fill_value=0)
    )
    category_proportions = category_amounts.div(
        total_amount.where(total_amount > 0), axis=0
    ).fillna(0)
    category_proportions = category_proportions.add_prefix(
        "category_"
    ).add_suffix("_proportion")

    profiles = pd.DataFrame(
        {
            "total_amount": total_amount,
            "transaction_count": transaction_count,
            "average_amount": average_amount.fillna(0),
        }
    )
    profiles = profiles.join(category_proportions)
    profiles.index.name = "period"

    return profiles
