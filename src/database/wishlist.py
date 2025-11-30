from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DECIMAL, String

from src.config.database import Base


class Wishlist(Base):
    __tablename__ = "wishlists"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    estimated_price: Mapped[Optional[DECIMAL]] = mapped_column(
        DECIMAL(10, 2), nullable=True
    )
    urgency: Mapped[Optional[str]] = mapped_column(
        String(50), default="low", nullable=True
    )
    priority: Mapped[Optional[str]] = mapped_column(
        String(50), default="medium", nullable=True
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False, default="want")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
