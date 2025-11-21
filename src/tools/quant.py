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


@tool(description="Check user balance")
def check_balance() -> dict[str, str]:
    writer = get_stream_writer()

    writer("Retrieving user balance..")
    with open(os.path.join(MEMORY_DIR, "semantic", "profile.json"), "r") as file:
        data = json.load(file)

    return {"status": "success", "balance": data["finance"].get("balance", 0)}


@tool(description="Update user balance")
def update_balance(amount: int, runtime: ToolRuntime) -> dict[str, str]:
    writer = get_stream_writer()

    with open(os.path.join(MEMORY_DIR, "semantic", "profile.json"), "r") as file:
        data = json.load(file)

    writer("Calculating current balance..")
    new_balance = data["finance"].get("balance", 0) + amount

    writer("Updating balance..")
    with open(os.path.join(MEMORY_DIR, "semantic", "profile.json"), "w") as file:
        data["finance"]["balance"] = new_balance
        data = json.dump(data, file, indent=4)

    return {"status": "success", "current_balance": new_balance}

@tool(description="Get user budget")
def check_budget() -> dict[str, dict]:
    writer = get_stream_writer()

    writer("Retrieving user budget..")
    with open(os.path.join(MEMORY_DIR, "semantic", "profile.json"), "r") as file:
        data = json.load(file)

    budget = data['finance'].get('budget', {})

    return {"status": "success", "user_budget": budget}

@tool(description="Update user budget")
def update_budget(
    living: int,
    transportation: int,
    food_n_drink: int,
    health_n_insurance: int,
    education: int,
    entertainment: int,
    miscellaneous: int,
    liabilities: int,
    saving_n_investment: int
    ):
    writer = get_stream_writer()

    with open(os.path.join(MEMORY_DIR, "semantic", "profile.json"), "r") as file:
        data = json.load(file)

    writer("Inserting new budget..")
    budget = {
      "living": living,
      "transportation": transportation,
      "food_&_drink": food_n_drink,
      "health_&_insurance": health_n_insurance,
      "education": education,
      "entertainment": entertainment,
      "miscellaneous": miscellaneous,
      "liabilities": liabilities,
      "saving_&_investment": saving_n_investment
    }

    writer("Updating budget..")
    with open(os.path.join(MEMORY_DIR, "semantic", "profile.json"), "w") as file:
        data["finance"]["budget"] = budget
        data = json.dump(data, file, indent=4)





def time_value_calculator():
    pass
