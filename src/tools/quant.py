from datetime import datetime
from decimal import Decimal

from langchain.tools import tool
from langgraph.config import get_stream_writer
from typing_extensions import Optional

from src.database import Session, Transaction


@tool("write_transaction")
def write_transaction(
    timestamp: str,
    amount: int,
    type: str,
    description: str,
    category: str,
    subcategory: Optional[str],
    notes: Optional[str],
) -> dict:
    """Insert a transaction into the database

    Args:
        timestamp (str): Transaction date
        amount (str): Amount of the transaction
        type (str): Transaction type (income or expense)
        description (str): The transaction description
        category (str): Transaction category
        subcategory (str): Optional sub-category based on the transaction category
        notes (str): Optional notes specified by the user

    Returns:
        dict: A dictionary containing the transaction record.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'summary' key with weather details.
              If 'error', includes an 'error_message' key.
    """

    writer = get_stream_writer()
    timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    amount = Decimal(amount)
    session = Session()

    writer("Preparing the data..")
    new_transaction = Transaction(
        timestamp=timestamp,
        amount=amount,
        type=type.lower(),
        description=description,
        category=category.lower(),
        subcategory=subcategory.lower(),
        notes=notes,
    )
    writer("Inserting transaction to the Database..")
    session.add(new_transaction)
    session.commit()
    session.close()

    return {
        "status": "success",
        "summary": (
            "Transaction recorded successfully..\n"
            f"Type: {type}\n"
            f"Amount: {amount}\n"
            f"Timestamp: {timestamp}\n"
            f"Description: {description}\n"
            f"Category: {category}\n"
            f"Sub Category: {subcategory}\n"
            f"Notes: {notes}"
        ),
    }


def time_value_calculator():
    pass
