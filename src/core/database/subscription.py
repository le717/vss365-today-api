from typing import Literal

from sqlalchemy.exc import DBAPIError, IntegrityError

from src.core.database import __connect_to_db

__all__ = [
    "subscription_email_create",
    "subscription_email_delete",
]


def subscription_email_create(addr: str) -> bool:
    """Add a subscription email address."""
    try:
        sql = "INSERT INTO emails (email) VALUES (:addr)"
        with __connect_to_db() as db:
            db.query(sql, addr=addr.lower())
        return True

    # That address aleady exists in the database.
    # However, to prevent data leakage, pretend it added
    except IntegrityError as exc:
        print(f"New subscription exception: {exc}")
        print(addr)
        return True

    # An error occurred trying to record the email
    except DBAPIError as exc:
        print(f"New subscription exception: {exc}")
        print(addr)
        return False


def subscription_email_delete(addr: str) -> Literal[True]:
    """Remove a subscription email address."""
    sql = "DELETE FROM emails WHERE email = :addr"
    with __connect_to_db() as db:
        db.query(sql, addr=addr)
    return True
