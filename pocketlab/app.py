from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from pocketlab.analytics import category_totals, load_expenses, monthly_totals, summarize_expenses
from pocketlab.config import APP_TITLE, DB_PATH, RAW_DATA_PATH
from pocketlab.db import init_db, insert_expense, load_expenses_from_db, seed_database

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["TITLE"] = APP_TITLE
#test

def ensure_database_seeded():
    init_db(DB_PATH)
    from pocketlab.db import connect_db

    conn = connect_db(DB_PATH)
    try:
        count = conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
    finally:
        conn.close()
    if count == 0:
        seed_database(RAW_DATA_PATH, DB_PATH)


@app.before_request
def initialize_app_state():
    ensure_database_seeded()


@app.route("/")
def dashboard():
    data = load_expenses_from_db(DB_PATH)
    summary = summarize_expenses(data)
    return render_template("dashboard.html", title=APP_TITLE, summary=summary)


@app.route("/expenses")
def expenses():
    data = load_expenses_from_db(DB_PATH)
    return render_template("expenses.html", title="Expenses", expenses=data)


@app.route("/api/expenses", methods=["GET", "POST"])
def api_expenses():
    if request.method == "GET":
        return jsonify(load_expenses_from_db(DB_PATH))

    payload = request.get_json(silent=True) or request.form.to_dict()
    date = (payload.get("date") or "").strip()
    category = (payload.get("category") or "").strip()
    amount_raw = payload.get("amount")
    description = (payload.get("description") or "").strip()

    if not date or not category or amount_raw in (None, ""):
        return jsonify({"error": "date, category, and amount are required"}), 400

    try:
        amount = float(amount_raw)
    except (TypeError, ValueError):
        return jsonify({"error": "amount must be a valid number"}), 400

    if amount < 0:
        return jsonify({"error": "amount cannot be negative"}), 400

    row = insert_expense(date=date, category=category, amount=amount, description=description, db_path=DB_PATH)
    return jsonify(row), 201


@app.route("/budget")
def budget():
    data = load_expenses_from_db(DB_PATH)
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
