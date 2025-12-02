import json
import os
from datetime import datetime
from decimal import Decimal

from langchain.tools import ToolRuntime, tool
from langgraph.config import get_stream_writer
from langgraph.types import Command
from sqlalchemy import desc, or_, select
from typing_extensions import Optional

from src.config.database import Session
from src.config.directory import MEMORY_DIR
from src.database import Transaction


@tool("read_transactions")
def read_transactions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    transaction_type: Optional[str] = None,
    category: Optional[str] = None,
    search_term: Optional[str] = None,
    limit: int = 10,
) -> dict:
    """
    Retrieve transaction records from the database with flexible filtering.

    Args:
        start_date (str, optional): Filter transactions starting from this date (YYYY-MM-DD).
        end_date (str, optional): Filter transactions up to this date (YYYY-MM-DD).
        transaction_type (str, optional): Filter by 'income' or 'expense'.
        category (str, optional): Filter by specific category (e.g., 'Food', 'Transport').
        search_term (str, optional): Search keyword in description, subcategory, or notes.
        limit (int): Max number of records to return. Defaults to 10.

    Returns:
        dict: A dictionary containing status, summary, and a list of transactions.
    """
    writer = get_stream_writer()
    session = Session()
    results = []

    try:
        writer("Querying transactions based on parameters...")

        # Start with a base query ordering by newest first
        stmt = select(Transaction).order_by(desc(Transaction.timestamp))

        # 1. Date Range Filtering
        if start_date:
            try:
                s_date = datetime.strptime(start_date, "%Y-%m-%d")
                stmt = stmt.where(Transaction.timestamp >= s_date)
            except ValueError:
                return {
                    "status": "error",
                    "error_message": "Invalid start_date format. Use YYYY-MM-DD.",
                }

        if end_date:
            try:
                e_date = datetime.strptime(end_date, "%Y-%m-%d")
                # Set time to end of day for inclusive comparison
                e_date = e_date.replace(hour=23, minute=59, second=59)
                stmt = stmt.where(Transaction.timestamp <= e_date)
            except ValueError:
                return {
                    "status": "error",
                    "error_message": "Invalid end_date format. Use YYYY-MM-DD.",
                }

        # 2. Type Filtering (Income/Expense)
        if transaction_type:
            stmt = stmt.where(Transaction.type == transaction_type.lower())

        # 3. Category Filtering
        if category:
            stmt = stmt.where(Transaction.category == category.lower())

        # 4. Keyword Search (Description, Subcategory, or Notes)
        if search_term:
            term = f"%{search_term.lower()}%"
            stmt = stmt.where(
                or_(
                    Transaction.description.ilike(term),
                    Transaction.subcategory.ilike(term),
                    Transaction.notes.ilike(term),
                )
            )

        # Apply Limit
        stmt = stmt.limit(limit)

        # Execute
        transactions = session.execute(stmt).scalars().all()
        session.close()

        if not transactions:
            return {
                "status": "success",
                "summary": "No transactions found matching criteria.",
                "transactions": [],
            }

        # Format Output
        for t in transactions:
            results.append(
                {
                    "id": t.id,
                    "date": t.timestamp.strftime("%Y-%m-%d"),
                    "amount": f"{t.currency} {t.amount}",
                    "type": t.type,
                    "category": f"{t.category}"
                    + (f" ({t.subcategory})" if t.subcategory else ""),
                    "description": t.description,
                    "notes": t.notes or "",
                }
            )

        summary_text = f"Found {len(results)} transactions."
        if start_date:
            summary_text += f" From {start_date}."
        if category:
            summary_text += f" Category: {category}."

        return {
            "status": "success",
            "summary": summary_text,
            "transactions": results,
        }

    except Exception as e:
        session.close()
        return {
            "status": "error",
            "error_message": f"Database query failed: {e}",
        }


def time_value_calculator(amount: str) -> dict:
    """
    Calculates the 'Life Hours' or time cost of a specific expense amount.
    Uses the user's average salary and a fixed real-time monthly conversion (720 hours)
    to determine the hourly rate of the user's life energy.

    Args:
        amount (str): The expense amount to calculate time value for (e.g. '120.50').

    Returns:
        dict: Contains the formatted insight string describing the time cost.
    """
    writer = get_stream_writer()

    try:
        clean_amount = amount.replace(",", "").replace("$", "").strip()
        clean_amount = "".join([c for c in clean_amount if c.isdigit() or c == "."])
        expense_amount = float(clean_amount)
    except ValueError:
        return {"status": "error", "error_message": "Invalid amount provided."}

    with open(os.path.join(MEMORY_DIR, "semantic", "profile.json"), "r") as file:
        data = json.load(file)

    finance_data = data.get("finance", {})
    avg_salary = finance_data.get("avg_salary", 0)
    currency = data.get("profile", {}).get("user_currency", "USD")

    if avg_salary <= 0:
        return {
            "status": "error",
            "error_message": "Average salary is not set in your profile. Please set your income first to use this feature.",
        }

    TOTAL_HOURS_PER_MONTH = 720

    hourly_rate = avg_salary / TOTAL_HOURS_PER_MONTH

    if hourly_rate <= 0:
        return {
            "status": "error",
            "error_message": "Calculated hourly rate is invalid.",
        }

    hours_cost = expense_amount / hourly_rate

    writer("Calculating time value...")

    if hours_cost < 1:
        time_str = f"{int(hours_cost * 60)} minutes"
    elif hours_cost < 24:
        time_str = f"{hours_cost:.1f} hours"
    else:
        days = hours_cost / 24
        time_str = f"{days:.1f} days"

    insight = f"{currency} {expense_amount:,.2f} is equivalent to {time_str} of your real life time."

    return {
        "insight": insight,
        "hours_cost": hours_cost,
        "hourly_rate_used": hourly_rate,
    }


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

        if type.lower() == "expense":
            return {
                "status": "success",
                "time_value_calculator": time_value_calculator(amount),
                "summary": (
                    "Transaction recorded successfully.\n"
                    f"Type: {type.upper()} | Amount: {currency.upper()} {amount_d}\n"
                    f"Description: {description}\n"
                    f"Category: {category.title()} ({subcategory.title() if subcategory else 'N/A'})\n"
                    f"Timestamp: {timestamp_dt.strftime('%Y-%m-%d')}"
                ),
            }
        else:
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

    budget = data["finance"].get("budget", {})

    return {"status": "success", "user_budget": budget}


@tool(description="Update user budget")
def update_budget(budget: dict):
    writer = get_stream_writer()

    with open(os.path.join(MEMORY_DIR, "semantic", "profile.json"), "r") as file:
        data = json.load(file)

    writer("Inserting new budget..")
    budget = budget

    writer("Updating budget..")
    with open(os.path.join(MEMORY_DIR, "semantic", "profile.json"), "w") as file:
        data["finance"]["budget"] = budget
        data = json.dump(data, file, indent=4)


@tool(description="Retrieve user average income")
def get_avg_income() -> dict[str, str]:
    writer = get_stream_writer()

    writer("Retrieving user average income..")
    with open(os.path.join(MEMORY_DIR, "semantic", "profile.json"), "r") as file:
        data = json.load(file)

    return {"status": "success", "avg_income": data["finance"].get("avg_salary", 0)}
