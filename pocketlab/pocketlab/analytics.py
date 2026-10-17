from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_PATH = BASE_DIR / "data" / "raw" / "expenses.csv"


def _ensure_dataframe(data) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        return data.copy()
    if isinstance(data, pd.Series):
        return data.to_frame().reset_index()
    if isinstance(data, (list, tuple)):
        return pd.DataFrame(data)
    if isinstance(data, (str, Path)):
        return load_expenses(data)
    raise TypeError(f"Unsupported expense data type: {type(data)!r}")


def _normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    rename_map = {
        "amount": "amount",
        "total": "amount",
        "expense": "amount",
        "value": "amount",
        "cost": "amount",
        "date": "date",
        "spent_on": "date",
        "category": "category",
        "type": "category",
        "kind": "category",
        "description": "description",
        "note": "description",
        "memo": "description",
    }
    column_names = {str(column).strip().lower(): column for column in normalized.columns}
    for original_name, canonical_name in list(rename_map.items()):
        if original_name in column_names:
            normalized = normalized.rename(columns={column_names[original_name]: canonical_name})
    if "date" not in normalized.columns:
        for candidate in ("transaction_date", "spent_at", "posted_at", "day"):
            if candidate in column_names:
                normalized = normalized.rename(columns={column_names[candidate]: "date"})
    if "category" not in normalized.columns:
        for candidate in ("label", "merchant", "shop"):
            if candidate in column_names:
                normalized = normalized.rename(columns={column_names[candidate]: "category"})
    if "amount" not in normalized.columns:
        for candidate in ("amount_usd", "price"):
            if candidate in column_names:
                normalized = normalized.rename(columns={column_names[candidate]: "amount"})
    normalized.columns = [str(col).strip().lower() for col in normalized.columns]
    return normalized


def load_expenses(path: str | Path | None = None) -> pd.DataFrame:
    """Read expense data from a CSV file and normalize it for downstream aggregation."""
    target = Path(path) if path is not None else DEFAULT_DATA_PATH
    if not target.exists():
        raise FileNotFoundError(f"Expense data file not found: {target}")

    frame = pd.read_csv(target)
    normalized = _normalize_columns(frame)

    if "date" in normalized.columns:
        normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce")
    else:
        normalized["date"] = pd.NaT
    if "amount" in normalized.columns:
        normalized["amount"] = pd.to_numeric(normalized["amount"], errors="coerce")
    else:
        normalized["amount"] = pd.NA
    if "category" not in normalized.columns:
        normalized["category"] = "Other"
    normalized["category"] = normalized["category"].fillna("Other").astype(str).str.strip()
    if "description" not in normalized.columns:
        normalized["description"] = ""
    normalized["description"] = normalized["description"].fillna("").astype(str)

    normalized = normalized.dropna(subset=["date", "amount", "category"]).copy()
    normalized = normalized.sort_values("date").reset_index(drop=True)
    normalized["month"] = normalized["date"].dt.to_period("M").astype(str)
    return normalized


def total_spend(expenses) -> float:
    """Return the sum of all expense amounts."""
    frame = _ensure_dataframe(expenses)
    frame = _normalize_columns(frame)
    if "amount" not in frame.columns:
        return 0.0
    return float(pd.to_numeric(frame["amount"], errors="coerce").sum())


def average_expense(expenses) -> float:
    """Return the average expense amount."""
    frame = _ensure_dataframe(expenses)
    frame = _normalize_columns(frame)
    if "amount" not in frame.columns:
        return 0.0
    values = pd.to_numeric(frame["amount"], errors="coerce")
    return float(values.mean()) if not values.empty else 0.0


def monthly_totals(expenses) -> pd.DataFrame:
    """Aggregate spending by month."""
    frame = _ensure_dataframe(expenses)
    frame = _normalize_columns(frame)
    if "amount" not in frame.columns:
        return pd.DataFrame(columns=["month", "amount"])
    if "month" not in frame.columns:
        if "date" in frame.columns:
            frame["month"] = pd.to_datetime(frame["date"], errors="coerce").dt.to_period("M").astype(str)
        else:
            frame["month"] = "unknown"
    return (
        frame.groupby("month", as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "total"})
        .sort_values("month")
        .reset_index(drop=True)
    )


def category_totals(expenses) -> pd.DataFrame:
    """Aggregate spending by category."""
    frame = _ensure_dataframe(expenses)
    frame = _normalize_columns(frame)
    if "amount" not in frame.columns:
        return pd.DataFrame(columns=["category", "amount"])
    if "category" not in frame.columns:
        frame["category"] = "Other"
    grouped = (
        frame.groupby("category", as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "total"})
        .sort_values("total", ascending=False)
        .reset_index(drop=True)
    )
    return grouped


def top_categories(expenses, n: int = 5) -> pd.DataFrame:
    """Return the biggest expense categories."""
    return category_totals(expenses).head(n).reset_index(drop=True)


def summarize_expenses(expenses) -> dict:
    """Return a compact summary of the expense data."""
    frame = _ensure_dataframe(expenses)
    frame = _normalize_columns(frame)
    spend = total_spend(frame)
    values = pd.to_numeric(frame.get("amount", pd.Series(dtype=float)), errors="coerce")
    transaction_count = int(len(values.dropna()))
    average = float(values.mean()) if not values.empty and values.notna().any() else 0.0
    top_category = category_totals(frame).iloc[0]["category"] if not category_totals(frame).empty else "N/A"
    return {
        "total_spend": spend,
        "average_expense": average,
        "transaction_count": transaction_count,
        "top_category": top_category,
        "categories": category_totals(frame).to_dict(orient="records"),
        "monthly": monthly_totals(frame).to_dict(orient="records"),
    }


def budget_status(expenses, budget: float = 3000.0) -> dict:
    """Compare total spend against a monthly target budget."""
    spend = total_spend(expenses)
    remaining = float(budget) - spend
    percent_used = (spend / float(budget)) * 100 if float(budget) else 0.0
    return {
        "budget": float(budget),
        "spent": spend,
        "remaining": remaining,
        "percent_used": percent_used,
        "is_over_budget": spend > float(budget),
    }


def monthly_change(expenses) -> dict:
    """Measure changes between the most recent and previous month totals."""
    monthly = monthly_totals(expenses)
    if monthly.empty:
        return {"current_month": 0.0, "previous_month": 0.0, "delta": 0.0}
    recent = monthly.iloc[-1]["total"] if "total" in monthly.columns else 0.0
    previous = monthly.iloc[-2]["total"] if len(monthly) > 1 else recent
    return {
        "current_month": float(recent),
        "previous_month": float(previous),
        "delta": float(recent - previous),
    }


def largest_expense(expenses):
    frame = _ensure_dataframe(expenses)
    frame = _normalize_columns(frame)
    if "amount" not in frame.columns or frame.empty:
        return None
    row = frame.loc[frame["amount"].idxmax()]
    return {"date": row.get("date"), "category": row.get("category"), "amount": float(row["amount"])}


def get_summary(expenses):
    return summarize_expenses(expenses)


get_expenses = load_expenses
sum_expenses = total_spend
category_summary = category_totals
spending_by_month = monthly_totals
expense_summary = summarize_expenses
check_budget = budget_status


__all__ = [
    "DEFAULT_DATA_PATH",
    "average_expense",
    "budget_status",
    "category_summary",
    "category_totals",
    "check_budget",
    "expense_summary",
    "get_expenses",
    "get_summary",
    "largest_expense",
    "load_expenses",
    "monthly_change",
    "monthly_totals",
    "spending_by_month",
    "sum_expenses",
    "summarize_expenses",
    "top_categories",
    "total_spend",
]
