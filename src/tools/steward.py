from decimal import Decimal

from langchain.tools import tool
from langgraph.config import get_stream_writer
from typing_extensions import Any, Dict, Optional

from src.config.database import Session
from src.database import Wishlist


@tool
def append_wishlist(
    item_name: str,
    estimated_price: str,
    urgency: str = "low",
    priority: str = "low",
    item_type: str = "want",
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Add an item to the user's wishlist in the database.

    Args:
        item_name (str): Name of the item.
        estimated_price (str): Numeric cost of the item.
        urgency (str): User's perceived urgency ('high', 'medium', 'low').
        priority (str): Calculated financial priority ('high', 'medium', 'low').
        item_type (str): 'need' or 'want'.
        notes (str): Rationale or details.
    """
    writer = get_stream_writer()
    session = Session()
    try:
        price = Decimal(estimated_price) if estimated_price else None

        new_item = Wishlist(
            item_name=item_name,
            estimated_price=price,
            urgency=urgency.lower(),
            priority=priority.lower(),
            type=item_type.lower(),
            status="active",
            notes=notes,
        )
        session.add(new_item)

        writer(f"Adding '{item_name}' to wishlist...")
        session.commit()
        return {"status": "success", "summary": f"Added '{item_name}' to wishlist."}
    except Exception as e:
        session.rollback()
        return {"status": "error", "error_message": str(e)}
    finally:
        session.close()


@tool
def update_wishlist_status(
    item_name: str,
    new_status: str,
) -> Dict[str, Any]:
    """
    Update the status of a wishlist item (e.g., mark as purchased).

    Args:
        item_name (str): The name of the item.
        new_status (str): 'purchased', 'removed', or 'active'.
    """
    session = Session()
    try:
        stmt = select(Wishlist).where(Wishlist.item_name.ilike(f"%{item_name}%"))
        item = session.execute(stmt).scalars().first()

        if not item:
            return {
                "status": "error",
                "error_message": f"Item '{item_name}' not found.",
            }

        item.status = new_status.lower()
        session.commit()

        return {
            "status": "success",
            "summary": f"Updated '{item.item_name}' status to '{new_status}'.",
        }
    except Exception as e:
        session.rollback()
        return {"status": "error", "error_message": str(e)}
    finally:
        session.close()


@tool
def get_user_wishlist(status: str | None = "active") -> Dict[str, Any]:
    """
    Retrieve wishlist items filtered by status.
    """
    writer = get_stream_writer()
    session = Session()
    try:
        if status is None:
            items = session.query(Wishlist).all()
        else:
            items = session.query(Wishlist).filter(Wishlist.status == status).all()

        writer(f"Retrieving all user wishlists...")
        result = []
        for i in items:
            result.append(
                {
                    "id": i.id,
                    "item": i.item_name,
                    "price": str(i.estimated_price) if i.estimated_price else "N/A",
                    "urgency": i.urgency,
                    "priority": i.priority,
                    "type": i.type,
                    "notes": i.notes,
                }
            )

        return {"status": "success", "wishlist": result}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
    finally:
        session.close()
