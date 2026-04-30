from typing import Optional
from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DECIMAL

from src.config.database import Base

class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Wallet Details
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    balance: Mapped[DECIMAL] = mapped_column(DECIMAL(15, 2), default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)