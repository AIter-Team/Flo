from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from langchain.tools import tool
from langgraph.config import get_stream_writer

from src.config.database import Session
from src.database import Debt, Installment, Liability, Subscription


@tool("insert_debt")
def insert_debt(
    name: str,
    total_amount: str,
    interest_rate: Optional[str],
    amount_paid: str = "0",
    min_monthly_payment: Optional[str] = None,
    payment_due_day: Optional[int] = None,
    due_date: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Insert a new high-interest debt (loan, credit card) into the database.
    This tool is essential for Flo's Debt Destroyer feature (Avalanche Method).

    Args:
        name (str): A descriptive name for the debt (e.g., 'Credit Card A').
        total_amount (str): The initial total amount of the debt.
        interest_rate (str): The Annual Percentage Rate (APR) as a decimal (e.g., '0.18' for 18%).
        amount_paid (str): The total amount already paid (default is '0').
        min_monthly_payment (str): The minimum required monthly payment.
        payment_due_day (int): The day of the month the payment is due (1-31).
        due_date (str): Optional final due date in 'YYYY-MM-DD HH:MM:SS' format.
        notes (str): Optional notes specified by the user.

    Returns:
        dict: Status of the insertion.
    """
    writer = get_stream_writer()
    session = Session()

    try:
        total_amount_d = Decimal(total_amount)
        amount_paid_d = Decimal(amount_paid)
        interest_rate_d = Decimal(interest_rate) if interest_rate else None
        min_monthly_payment_d = (
            Decimal(min_monthly_payment) if min_monthly_payment else None
        )
        due_date_dt = (
            datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S") if due_date else None
        )

        writer("Preparing to insert new Debt entity...")

        new_debt = Debt(
            total_amount=total_amount_d,
            amount_paid=amount_paid_d,
            interest_rate=interest_rate_d,
            min_monthly_payment=min_monthly_payment_d,
            payment_due_day=payment_due_day,
            due_date=due_date_dt,
        )
        session.add(new_debt)
        session.flush()

        debt_id = new_debt.id

        parent = Liability(
            name=name, liability_type="debt", reference_id=debt_id, notes=notes
        )
        session.add(parent)
        session.commit()
        session.close()

        return {
            "status": "success",
            "summary": f"Debt '{name}' (Interest: {interest_rate_d}) recorded successfully. ID: {debt_id}",
        }
    except Exception as e:
        session.rollback()
        session.close()
        return {"status": "error", "error_message": f"Failed to insert Debt: {e}"}


@tool("insert_installment")
def insert_installment(
    item_name: str,
    original_price: str,
    monthly_payment: str,
    total_installments: int,
    installments_paid: int = 0,
    payment_due_day: Optional[int] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Insert a new installment plan or Buy Now Pay Later (BNPL) item.
    This tool is required for Flo's Installment Impact analysis.

    Args:
        item_name (str): Name of the item being purchased on installment.
        original_price (str): The full original price of the item.
        monthly_payment (str): The fixed payment amount per month.
        total_installments (int): The total number of payments in the plan.
        installments_paid (int): The number of installments already paid (default is 0).
        payment_due_day (int): The day of the month the payment is due (1-31).
        notes (str): Optional notes specified by the user.

    Returns:
        dict: Status of the insertion.
    """
    writer = get_stream_writer()
    session = Session()

    try:
        original_price_d = Decimal(original_price)
        monthly_payment_d = Decimal(monthly_payment)

        writer("Preparing to insert new Installment entity...")

        new_installment = Installment(
            original_price=original_price_d,
            monthly_payment=monthly_payment_d,
            total_installments=total_installments,
            installments_paid=installments_paid,
            payment_due_day=payment_due_day,
        )
        session.add(new_installment)
        session.flush()

        installments_id = new_installment.id

        parent = Liability(
            name=item_name,
            liability_type="installment",
            reference_id=installments_id,
            notes=notes,
        )
        session.add(parent)
        session.commit()
        session.close()

        return {
            "status": "success",
            "summary": (
                f"Installment for '{item_name}' recorded successfully. "
                f"Total payments: {total_installments}. ID: {installments_id}"
            ),
        }
    except Exception as e:
        session.rollback()
        session.close()
        return {
            "status": "error",
            "error_message": f"Failed to insert Installment: {e}",
        }


@tool("insert_subscription")
def insert_subscription(
    name: str,
    monthly_cost: str,
    billing_cycle: str = "monthly",
    next_billing_date: Optional[str] = None,
    last_usage_days: Optional[int] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Insert a new recurring subscription service.

    Args:
        name (str): Name of the subscription (e.g., 'Netflix', 'Gym Membership').
        monthly_cost (str): The recurring cost converted to a monthly basis.
        billing_cycle (str): The frequency of billing (e.g., 'monthly', 'yearly', 'weekly').
        next_billing_date (str): Optional date for the next payment in 'YYYY-MM-DD HH:MM:SS' format.
        last_usage_days (int): The number of days since the service was last used.
        notes (str): Optional notes specified by the user.

    Returns:
        dict: Status of the insertion.
    """
    writer = get_stream_writer()
    session = Session()

    try:
        monthly_cost_d = Decimal(monthly_cost)
        next_billing_date_dt = (
            datetime.strptime(next_billing_date, "%Y-%m-%d %H:%M:%S")
            if next_billing_date
            else None
        )

        writer("Preparing to insert new Subscription entity...")

        new_subscription = Subscription(
            monthly_cost=monthly_cost_d,
            billing_cycle=billing_cycle.lower(),
            next_billing_date=next_billing_date_dt,
            last_usage_days=last_usage_days,
        )
        session.add(new_subscription)
        session.flush()

        subscription_id = new_subscription.id

        parent = Liability(
            name=name,
            liability_type="subscription",
            reference_id=subscription_id,
            notes=notes,
        )
        session.add(parent)
        session.commit()
        session.close()

        return {
            "status": "success",
            "summary": (
                f"Subscription '{name}' (Cost: {monthly_cost_d} per month) recorded successfully. "
                f"Next bill: {next_billing_date_dt.date() if next_billing_date_dt else 'N/A'}. ID: {subscription_id}"
            ),
        }
    except Exception as e:
        session.rollback()
        session.close()
        return {
            "status": "error",
            "error_message": f"Failed to insert Subscription: {e}",
        }


@tool("get_user_liabilities")
def get_user_liabilities() -> Dict[str, Any]:
    """
    Retrieves all liabilities (debts, installments, and subscriptions) associated with the user.

    Queries the central 'liabilities' table and joins with the specific liability tables
    (debts, installments, subscriptions) to provide full details for each record.

    Returns:
        Dict[str, Any]: A dictionary containing a list of all liabilities, categorized
                        by their type ('debt', 'installment', 'subscription').
    """
    session = Session()
    liabilities_data = {"debt": [], "installment": [], "subscription": []}

    writer = get_stream_writer()
    writer("Retrieve user liabilities..")
    try:
        # 1. Query all entries from the main Liability table
        all_liabilities = session.query(Liability).all()

        for liability in all_liabilities:
            details = None

            # 2. Fetch details based on liability type and reference_id
            if liability.liability_type == "debt":
                details = (
                    session.query(Debt)
                    .filter(Debt.id == liability.reference_id)
                    .first()
                )
            elif liability.liability_type == "installment":
                details = (
                    session.query(Installment)
                    .filter(Installment.id == liability.reference_id)
                    .first()
                )
            elif liability.liability_type == "subscription":
                details = (
                    session.query(Subscription)
                    .filter(Subscription.id == liability.reference_id)
                    .first()
                )

            # 3. Combine main liability data with specific details
            if details:
                # Convert ORM object to a dictionary for a clean return structure
                liability_entry = {
                    "id": liability.id,
                    "name": liability.name,
                    "type": liability.liability_type,
                    "notes": liability.notes,
                    **{
                        k: v.isoformat() if isinstance(v, datetime) else str(v)
                        for k, v in details.__dict__.items()
                        if not k.startswith("_") and k != "id"
                    },
                }
                liabilities_data[liability.liability_type].append(liability_entry)

        session.close()
        return {
            "status": "success",
            "summary": "Successfully retrieved all user liabilities.",
            "data": liabilities_data,
        }

    except Exception as e:
        session.close()
        return {
            "status": "error",
            "error_message": f"Failed to retrieve liabilities: {e}",
        }
