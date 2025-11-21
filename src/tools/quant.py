import json
import os
from datetime import datetime
from decimal import Decimal

from langchain.tools import ToolRuntime, tool
from langgraph.config import get_stream_writer
from langgraph.types import Command
from typing_extensions import Optional

from src.config import MEMORY_DIR, Session
from src.database import Transaction


@tool("write_transaction")
def write_transaction(
    timestamp: str,
    amount: str,
    currency: str,
    type: str,
    description: str,
    category: str,
    subcategory: Optional[str],
    notes: Optional[str],
) -> dict:
    """Insert a transaction into the database

    Args:
        timestamp (str): Transaction date in 'YYYY-MM-DD HH:MM:SS' format.
        amount (str): Amount of the transaction (e.g., '120.50').
        currency (str): Currency used (USD, IDR, EUR, GBP, etc.).
        type (str): Transaction type (income or expense).
        description (str): The transaction description.
        category (str): Transaction category.
        subcategory (str): Optional sub-category based on the transaction category.
        notes (str): Optional notes specified by the user.

    Returns:
        dict: A dictionary containing the transaction record status.
    """
    writer = get_stream_writer()
    session = Session()

    try:
        timestamp_dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        amount_d = Decimal(amount)

        writer("Preparing the data...")
        new_transaction = Transaction(
            timestamp=timestamp_dt,
            amount=amount_d,
            currency=currency.upper(),
            type=type.lower(),
            description=description,
            category=category.lower(),
            subcategory=subcategory.lower() if subcategory else None,
            notes=notes,
        )

        writer("Inserting transaction to the Database...")
        session.add(new_transaction)
        session.commit()
        session.close()

        return {
            "status": "success",
            "summary": (
                "Transaction recorded successfully.\n"
                f"Type: {type.upper()} | Amount: {currency.upper()} {amount_d}\n"
                f"Description: {description}\n"
                f"Category: {category.title()} ({subcategory.title() if subcategory else 'N/A'})\n"
                f"Timestamp: {timestamp_dt.strftime('%Y-%m-%d')}"
            ),
        }
    except Exception as e:
        session.rollback()
        session.close()
        return {
            "status": "error",
            "error_message": f"Failed to insert transaction: {e}",
        }


@tool(description="Update user balance")
def update_balance(amount: int, runtime: ToolRuntime) -> tuple[dict[str, str], Command]:
    writer = get_stream_writer()

    with open(os.path.join(MEMORY_DIR, "semantic", "profile.json"), "r") as file:
        data = json.load(file)

    writer("Calculating current balance..")
    new_balance = data["profile"].get("user_balance", 0) + amount

    writer("Updating balance..")
    with open(os.path.join(MEMORY_DIR, "semantic", "profile.json"), "w") as file:
        data["profile"]["user_balance"] = new_balance
        data = json.dump(data, file, indent=4)

    return {"status": "success", "current_balance": new_balance}, Command(
        update={"user_balance": new_balance}
    )


def time_value_calculator():
    pass
