from .config import DB_PATH, RAW_DATA_PATH
from .db import init_db, seed_database


def initialize_seed():
    init_db(DB_PATH)
    seed_database(RAW_DATA_PATH, DB_PATH)
    return DB_PATH


if __name__ == "__main__":
    initialize_seed()
    print("Database initialized.")
