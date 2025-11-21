from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DECIMAL, TIMESTAMP, Integer, String

from src.config.db_config import Base


class Liability(Base):
    __tablename__ = "liabilities"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    liability_type: Mapped[str] = mapped_column(String(50), nullable=False)

    reference_id: Mapped[int] = mapped_column(Integer, nullable=False)

    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)


class Debt(Base):
    __tablename__ = "debts"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    total_amount: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    amount_paid: Mapped[DECIMAL] = mapped_column(
        DECIMAL(10, 2), nullable=False, default=0
    )

    interest_rate: Mapped[Optional[DECIMAL]] = mapped_column(
        DECIMAL(5, 4), nullable=True
    )

    min_monthly_payment: Mapped[Optional[DECIMAL]] = mapped_column(
        DECIMAL(10, 2), nullable=True
    )
    payment_due_day: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(), nullable=True)


class Installment(Base):
    __tablename__ = "installments"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    original_price: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    monthly_payment: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)

    total_installments: Mapped[int] = mapped_column(Integer, nullable=False)
    installments_paid: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    payment_due_day: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class Subscription(Base):
    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    monthly_cost: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    billing_cycle: Mapped[str] = mapped_column(
        String(50), nullable=False, default="monthly"
    )
    next_billing_date: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(), nullable=True
    )

    last_usage_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
