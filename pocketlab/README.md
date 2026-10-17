# PocketLab

PocketLab is a lightweight expense dashboard built around a CSV-backed analysis workflow and a small Flask app.

## Quick start

1. Install dependencies:
   `py -3 -m pip install -r requirements.txt`
2. Initialize the database:
   `py -3 -c "from pocketlab.seed import initialize_seed; initialize_seed()"`
3. Run the app:
   `py -3 app.py`

## Project layout

- `data/raw/expenses.csv` stores the raw expense data.
- `pocketlab/analytics.py` performs cleaning and aggregate calculations.
- `pocketlab/insights.py` creates summary insights.
- `pocketlab/charts.py` generates plots.
- `app.py` exposes the Flask dashboard routes.
