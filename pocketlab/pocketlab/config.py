from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "expenses.csv"
DB_PATH = DATA_DIR / "pocketlab.db"

APP_TITLE = "PocketLab"
