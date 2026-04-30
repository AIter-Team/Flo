from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DECIMAL, JSON, TIMESTAMP, Boolean, Integer, String

from src.config.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user_name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    occupation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    marital_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    user_language: Mapped[str] = mapped_column(String(50), default="English", nullable=False)
    user_currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    
    risk_tolerance: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    balance: Mapped[DECIMAL] = mapped_column(DECIMAL(15, 2), default=0, nullable=False)
    avg_income: Mapped[DECIMAL] = mapped_column(DECIMAL(15, 2), default=0, nullable=False)

    budget: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )