import os.path
import sqlite3
from typing import Dict, List, Optional

from src.core.config import load_app_config


__all__ = [
    "create_new_database",
    "create_prompt",
    "get_prompt_by_date",
    "get_prompt_years",
    "update_prompt"
]


def __dict_factory(cursor, row):
    """https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.row_factory"""  # noqa
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def __flatten_tuple_list(tup) -> list:
    """Flatten a list of tuples into a list of actual data."""
    return [item[0] for item in tup]


def __connect_to_db() -> sqlite3.Connection:
    """Create a connection to the database."""
    config = load_app_config()
    conn = sqlite3.connect(config["DB_PATH"])
    conn.row_factory = __dict_factory
    return conn


def create_new_database() -> Optional:
    """Create a new database if needed."""
    try:
        # If the database exists and is loaded, this will succeed
        sql = "SELECT COUNT(*) FROM writers"
        with __connect_to_db() as db:
            db.execute(sql)

    # The database doesn't exist
    except sqlite3.OperationalError:
        # Get the db schema
        schema = os.path.abspath(
            os.path.join("db", "schema.sql")
        )
        with open(schema, "rt") as f:
            sql = f.read()

        # Create the database according to the schema
        with __connect_to_db() as db:
            db.executescript(sql)


def create_prompt(prompt: Dict[str, Optional[str]]) -> bool:
    """Add a prompt to the database."""
    sql = """
    INSERT INTO tweets (
        tweet_id, date, uid, content, word, media
    )
    VALUES (
        :tweet_id, :date, :uid, :content, :word, :media
    )
    """
    try:
        with __connect_to_db() as db:
            db.execute(sql, prompt)
            return True

    # A prompt with this ID already exists
    except sqlite3.IntegrityError as exc:
        print(f"Prompt creation exception: {exc}")
        print(prompt)
        return False


def find_existing_prompt(prompt_id: str) -> bool:
    """Find an existing prompt."""
    sql = "SELECT 1 FROM tweets WHERE tweet_id = :tweet_id"
    with __connect_to_db() as db:
        return bool(db.execute(sql, {"tweet_id": prompt_id}).fetchone())


def get_prompt_years() -> List[str]:
    """Get a list of years of recorded prompts."""
    sql = """
    SELECT DISTINCT SUBSTR(date, 1, 4)
    FROM writer_dates
    WHERE SUBSTR(date, 1, 4) <= strftime('%Y','now')
    ORDER BY date ASC
    """
    with __connect_to_db() as db:
        r = db.execute(sql).fetchall()
    return __flatten_tuple_list(r)


def get_prompt_by_date(date: str) -> List[sqlite3.Row]:
    """Get a prompt tweet by the date it was posted."""
    sql = """
    SELECT tweets.*, writers.handle AS writer_handle
    FROM tweets
        JOIN writers ON writers.uid = tweets.uid
    WHERE tweets.date = :date
        AND :date <= date('now')
    """
    with __connect_to_db() as db:
        return db.execute(sql, {"date": date}).fetchall()


def update_prompt(prompt: Dict[str, Optional[str]]) -> bool:
    """Update an exising prompt in the database."""
    sql = """
    UPDATE tweets
    SET
        tweet_id = :tweet_id,
        date = :date,
        content = :content,
        word = :word,
        media =  :media
    WHERE tweet_id = :tweet_id
    """
    # try:
    with __connect_to_db() as db:
        db.execute(sql, prompt)
        return True

    # # A prompt with this ID already exists
    # except sqlite3.IntegrityError as exc:
    #     print(f"Prompt creation exception: {exc}")
    #     print(prompt)
    #     return False