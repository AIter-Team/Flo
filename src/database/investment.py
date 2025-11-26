from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DECIMAL, TIMESTAMP, Integer, String

from src.config.database import Base


class Investment(Base):
    __tablename__ = "investments"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    investment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reference_id: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="USD")
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)


class Asset(Base):
    """
    Represents tradable assets like Stocks, Crypto, ETFs.
    """
    __tablename__ = "assets"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity: Mapped[DECIMAL] = mapped_column(DECIMAL(18, 8), nullable=False)
    
    # UPDATED: Split average price into USD and User Currency
    average_buy_price_usd: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    average_buy_price_user_currency: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    
    # Market price is usually tracked in USD global standard, but can be implied by currency
    current_market_price: Mapped[Optional[DECIMAL]] = mapped_column(DECIMAL(10, 2), nullable=True)


class FixedDeposit(Base):
    """
    Represents fixed income investments like Bonds, CDs.
    """
    __tablename__ = "fixed_deposits"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    principal_amount: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    interest_rate: Mapped[DECIMAL] = mapped_column(DECIMAL(5, 4), nullable=False)
    
    start_date: Mapped[datetime] = mapped_column(TIMESTAMP(), nullable=False)
    maturity_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(default=True)