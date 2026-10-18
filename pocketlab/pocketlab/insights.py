from __future__ import annotations

from pathlib import Path

from .analytics import category_totals, get_summary, load_expenses, monthly_totals


def compute_insights(expenses, budget: float | None = None):
    """Return a summary dictionary with spending insights and narrative."""
    if isinstance(expenses, (str, Path)):
        data = load_expenses(expenses)
    else:
        data = expenses

    summary = get_summary(data)
    categories = category_totals(data).head(5)
    monthly = monthly_totals(data)
    latest_month = float(monthly.iloc[-1]["total"]) if not monthly.empty else 0.0
    previous_month = float(monthly.iloc[-2]["total"]) if len(monthly) > 1 else latest_month
    monthly_delta = latest_month - previous_month

    if budget is not None:
        budget_used = (latest_month / float(budget)) * 100 if float(budget) else 0.0
    else:
        budget_used = None

    narrative = []
    if not categories.empty:
        top = categories.iloc[0]
        narrative.append(f"{top['category']} is your largest spend category at ${top['total']:.2f}.")
    if not monthly.empty:
        if monthly_delta > 0:
            trend = "up"
        elif monthly_delta < 0:
            trend = "down"
        else:
            trend = "unchanged"
        narrative.append(
            f"Your latest month is ${latest_month:.2f}, which is "
            f"${abs(monthly_delta):.2f} {trend} from the prior month."
        )
    if budget_used is not None:
        narrative.append(f"You have used {budget_used:.1f}% of your budget.")

    return {
        "summary": summary,
        "category_breakdown": categories.to_dict(orient="records"),
        "monthly_totals": monthly.to_dict(orient="records"),
        "latest_month_spend": latest_month,
        "previous_month_spend": previous_month,
        "monthly_change": monthly_delta,
        "budget_used_pct": budget_used,
        "narrative": narrative,
    }


def generate_insights(expenses, budget: float | None = None):
    return compute_insights(expenses, budget)


insights = compute_insights

__all__ = ["compute_insights", "generate_insights", "insights"]
