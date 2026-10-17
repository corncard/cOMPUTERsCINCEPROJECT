from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .analytics import category_totals, monthly_totals


def _require_frame(data):
    frame = data.copy() if hasattr(data, "copy") else data
    return frame


def category_chart(expenses, title: str = "Expenses by category", save_path: str | None = None):
    """Create a bar chart for spending by category."""
    grouped = category_totals(expenses)
    fig, ax = plt.subplots(figsize=(8, 5))
    if grouped.empty:
        ax.text(0.5, 0.5, "No expense data", ha="center", va="center")
        ax.axis("off")
    else:
        ax.bar(grouped["category"], grouped["total"], color="steelblue")
        ax.set_title(title)
        ax.set_xlabel("Category")
        ax.set_ylabel("Amount")
        fig.autofmt_xdate()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
    return fig


def monthly_chart(expenses, title: str = "Expenses by month", save_path: str | None = None):
    """Create a line chart for spending over time."""
    monthly = monthly_totals(expenses)
    fig, ax = plt.subplots(figsize=(8, 5))
    if monthly.empty:
        ax.text(0.5, 0.5, "No expense data", ha="center", va="center")
        ax.axis("off")
    else:
        ax.plot(monthly["month"], monthly["total"], marker="o", color="darkorange")
        ax.set_title(title)
        ax.set_xlabel("Month")
        ax.set_ylabel("Total spend")
        fig.autofmt_xdate()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
    return fig


def budget_chart(expenses, budget: float = 3000.0, title: str = "Budget progress", save_path: str | None = None):
    """Create a simple budget comparison chart."""
    total = float(sum(expenses["amount"]) if hasattr(expenses, "__getitem__") and "amount" in expenses.columns else 0.0)
    if hasattr(expenses, "sum"):
        total = float(expenses["amount"].sum()) if "amount" in getattr(expenses, "columns", []) else 0.0
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(["Spent", "Remaining"], [total, max(float(budget) - total, 0.0)], color=["crimson", "forestgreen"])
    ax.set_title(title)
    ax.set_ylabel("Amount")
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
    return fig


__all__ = ["budget_chart", "category_chart", "monthly_chart"]
