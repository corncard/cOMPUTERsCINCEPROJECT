import sqlite3
from pathlib import Path

from .config import DB_PATH


def connect_db(db_path: str | Path | None = None):
    """Return a connection to the project SQLite database."""
    target = Path(db_path) if db_path else DB_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str | Path | None = None):
    """Create the expenses table if it does not already exist."""
    conn = connect_db(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def seed_database(csv_path: str | Path | None = None, db_path: str | Path | None = None):
    """Populate the SQLite database with expenses from the CSV file."""
    from .analytics import load_expenses

    df = load_expenses(csv_path)
    conn = connect_db(db_path)
    try:
        conn.execute("DELETE FROM expenses")
        for row in df.to_dict(orient="records"):
            conn.execute(
                "INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
                (
                    row["date"].strftime("%Y-%m-%d"),
                    row["category"],
                    float(row["amount"]),
                    row.get("description", ""),
                ),
            )
        conn.commit()
    finally:
        conn.close()


def load_expenses_from_db(db_path: str | Path | None = None):
    """Fetch all expense rows from the database."""
    conn = connect_db(db_path)
    try:
        rows = conn.execute(
            "SELECT date, category, amount, description FROM expenses ORDER BY date"
        ).fetchall()
    finally:
        conn.close()
    return [dict(row) for row in rows]
