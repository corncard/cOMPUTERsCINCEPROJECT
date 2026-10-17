from __future__ import annotations

from flask import Flask, render_template

from pocketlab.analytics import category_totals, load_expenses, monthly_totals, summarize_expenses
from pocketlab.config import APP_TITLE, RAW_DATA_PATH

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["TITLE"] = APP_TITLE


@app.route("/")
def dashboard():
    data = load_expenses(RAW_DATA_PATH)
    summary = summarize_expenses(data)
    return render_template("dashboard.html", title=APP_TITLE, summary=summary)


@app.route("/expenses")
def expenses():
    data = load_expenses(RAW_DATA_PATH)
    return render_template("expenses.html", title="Expenses", expenses=data.to_dict(orient="records"))


@app.route("/budget")
def budget():
    data = load_expenses(RAW_DATA_PATH)
    summary = summarize_expenses(data)
    monthly = monthly_totals(data)
    categories = category_totals(data)
    return render_template(
        "budget.html",
        title="Budget",
        summary=summary,
        monthly=monthly.to_dict(orient="records"),
        categories=categories.to_dict(orient="records"),
    )


if __name__ == "__main__":
    app.run(debug=True)
