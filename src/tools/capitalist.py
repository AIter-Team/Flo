from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from langchain.tools import tool
from langgraph.config import get_stream_writer

from src.config.database import Session
from src.database import (
    Debt,
    Installment,
    Liability,
    Subscription,
    Asset,
    FixedDeposit,
    Investment,
)


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

@tool("insert_asset")
def insert_asset(
    name: str,
    symbol: str,
    quantity: str,
    average_buy_price_usd: str,
    average_buy_price_user_currency: str,
    currency: str = "USD",
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Insert a variable income asset (Stocks, Crypto, ETFs).

    Args:
        name (str): Display name (e.g., 'Apple Stock').
        symbol (str): Ticker symbol.
        quantity (str): Amount of units/shares.
        average_buy_price_usd (str): Average price paid per unit in USD.
        average_buy_price_user_currency (str): Average price paid per unit in User's local currency.
        currency (str): The local currency code (e.g., 'IDR', 'EUR').
        notes (str): Optional notes.
    """
    writer = get_stream_writer()
    session = Session()

    try:
        writer(f"Inserting Asset: {name} ({symbol})...")

        new_asset = Asset(
            symbol=symbol.upper(),
            quantity=Decimal(quantity),
            average_buy_price_usd=Decimal(average_buy_price_usd),
            average_buy_price_user_currency=Decimal(average_buy_price_user_currency),
            current_market_price=Decimal(average_buy_price_usd) # Default to USD price
        )
        session.add(new_asset)
        session.flush()

        new_investment = Investment(
            name=name,
            investment_type="asset",
            reference_id=new_asset.id,
            currency=currency.upper(),
            notes=notes
        )
        session.add(new_investment)
        session.commit()
        session.close()

        return {
            "status": "success",
            "summary": f"Asset '{name}' recorded. Qty: {quantity} | Avg USD: {average_buy_price_usd} | Avg {currency}: {average_buy_price_user_currency}"
        }
    except Exception as e:
        session.rollback()
        session.close()
        return {"status": "error", "error_message": f"Failed to insert Asset: {e}"}


@tool("insert_fixed_deposit")
def insert_fixed_deposit(
    name: str,
    principal_amount: str,
    interest_rate: str,
    start_date: str,
    maturity_date: Optional[str] = None,
    currency: str = "USD",
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Insert a fixed income investment (Bonds, CDs, Time Deposits).

    Args:
        name (str): Display name (e.g., 'Emergency Fund CD', 'Gov Bond').
        principal_amount (str): Total amount deposited/invested.
        interest_rate (str): Annual interest rate as decimal (e.g., '0.05' for 5%).
        start_date (str): Start date in 'YYYY-MM-DD'.
        maturity_date (str): Optional maturity date in 'YYYY-MM-DD'.
        currency (str): Currency code (default 'USD').
        notes (str): Optional notes.

    Returns:
        dict: Status of the insertion.
    """
    writer = get_stream_writer()
    session = Session()

    try:
        writer(f"Inserting Fixed Deposit: {name}...")

        # 1. Create Specific Fixed Deposit Record
        new_fd = FixedDeposit(
            principal_amount=Decimal(principal_amount),
            interest_rate=Decimal(interest_rate),
            start_date=datetime.strptime(start_date, "%Y-%m-%d"),
            maturity_date=datetime.strptime(maturity_date, "%Y-%m-%d") if maturity_date else None
        )
        session.add(new_fd)
        session.flush()

        # 2. Link to Main Investment Registry
        new_investment = Investment(
            name=name,
            investment_type="fixed_deposit",
            reference_id=new_fd.id,
            currency=currency.upper(),
            notes=notes
        )
        session.add(new_investment)
        session.commit()
        session.close()

        return {
            "status": "success",
            "summary": f"Fixed Deposit '{name}' recorded. Principal: {currency} {principal_amount} @ {interest_rate}."
        }
    except Exception as e:
        session.rollback()
        session.close()
        return {"status": "error", "error_message": f"Failed to insert Fixed Deposit: {e}"}

@tool("get_user_investments")
def get_user_investments() -> Dict[str, Any]:
    """
    Retrieves all investment holdings (Assets and Fixed Deposits).
    """
    session = Session()
    investments_data = {"asset": [], "fixed_deposit": []}
    writer = get_stream_writer()

    try:
        writer("Retrieving user investments...")
        all_investments = session.query(Investment).all()

        for inv in all_investments:
            details = None
            if inv.investment_type == "asset":
                details = session.query(Asset).filter(Asset.id == inv.reference_id).first()
            elif inv.investment_type == "fixed_deposit":
                details = session.query(FixedDeposit).filter(FixedDeposit.id == inv.reference_id).first()

            if details:
                # Merge generic Investment info with specific details
                entry = {
                    "id": inv.id,
                    "name": inv.name,
                    "type": inv.investment_type,
                    "currency": inv.currency,
                    "notes": inv.notes,
                    **{
                        k: v.isoformat() if isinstance(v, datetime) else str(v)
                        for k, v in details.__dict__.items()
                        if not k.startswith("_") and k != "id"
                    },
                }
                investments_data[inv.investment_type].append(entry)

        session.close()
        return {
            "status": "success",
            "summary": "Successfully retrieved portfolio.",
            "data": investments_data,
        }
    except Exception as e:
        session.close()
        return {"status": "error", "error_message": f"Failed to retrieve investments: {e}"}


@tool("update_asset")
def update_asset(
    name: str,
    quantity: Optional[str] = None,
    average_buy_price_usd: Optional[str] = None,
    average_buy_price_user_currency: Optional[str] = None,
    current_market_price: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update an existing Asset.
    
    Args:
        name (str): The exact name of the investment.
        quantity (str): New total quantity.
        average_buy_price_usd (str): New average buy price in USD.
        average_buy_price_user_currency (str): New average buy price in User Currency.
        current_market_price (str): New market price (USD).
        notes (str): Update notes.
    """
    writer = get_stream_writer()
    session = Session()

    try:
        investment = session.query(Investment).filter(
            Investment.name == name, 
            Investment.investment_type == "asset"
        ).first()

        if not investment:
            return {"status": "error", "error_message": f"Asset '{name}' not found."}

        asset = session.query(Asset).filter(Asset.id == investment.reference_id).first()
        changes = []

        if quantity:
            asset.quantity = Decimal(quantity)
            changes.append(f"Qty: {quantity}")
        if average_buy_price_usd:
            asset.average_buy_price_usd = Decimal(average_buy_price_usd)
            changes.append(f"Avg USD: {average_buy_price_usd}")
        if average_buy_price_user_currency:
            asset.average_buy_price_user_currency = Decimal(average_buy_price_user_currency)
            changes.append(f"Avg User Curr: {average_buy_price_user_currency}")
        if current_market_price:
            asset.current_market_price = Decimal(current_market_price)
            changes.append(f"Mkt Price: {current_market_price}")
        if notes:
            investment.notes = notes
            changes.append("Notes updated")

        session.commit()
        session.close()

        return {"status": "success", "summary": f"Updated '{name}': {', '.join(changes)}"}
    except Exception as e:
        session.rollback()
        session.close()
        return {"status": "error", "error_message": f"Update failed: {e}"}


@tool("update_fixed_deposit")
def update_fixed_deposit(
    name: str,
    principal_amount: Optional[str] = None,
    interest_rate: Optional[str] = None,
    maturity_date: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Update a Fixed Deposit (Bond/CD).
    
    Args:
        name (str): The exact name of the investment.
        principal_amount (str): New principal amount.
        interest_rate (str): New interest rate (decimal).
        maturity_date (str): New maturity date (YYYY-MM-DD).
        is_active (bool): Set to False to mark as matured/closed.
    """
    writer = get_stream_writer()
    session = Session()

    try:
        investment = session.query(Investment).filter(
            Investment.name == name, 
            Investment.investment_type == "fixed_deposit"
        ).first()

        if not investment:
            return {"status": "error", "error_message": f"Fixed Deposit '{name}' not found."}

        fd = session.query(FixedDeposit).filter(FixedDeposit.id == investment.reference_id).first()

        changes = []
        if principal_amount:
            fd.principal_amount = Decimal(principal_amount)
            changes.append(f"Principal: {principal_amount}")
        if interest_rate:
            fd.interest_rate = Decimal(interest_rate)
            changes.append(f"Rate: {interest_rate}")
        if maturity_date:
            fd.maturity_date = datetime.strptime(maturity_date, "%Y-%m-%d")
            changes.append(f"Maturity: {maturity_date}")
        if is_active is not None:
            fd.is_active = is_active
            changes.append(f"Active: {is_active}")

        session.commit()
        session.close()

        return {
            "status": "success", 
            "summary": f"Updated '{name}': {', '.join(changes)}"
        }
    except Exception as e:
        session.rollback()
        session.close()
        return {"status": "error", "error_message": f"Update failed: {e}"}