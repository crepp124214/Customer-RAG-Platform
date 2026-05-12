from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, TimestampMixin, generate_id


class Product(TimestampMixin, Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")

    manuals = relationship("ProductManual", back_populates="product", cascade="all, delete-orphan")
    specs = relationship("ProductSpec", back_populates="product", cascade="all, delete-orphan")
    fault_sops = relationship("FaultSOP", back_populates="product", cascade="all, delete-orphan")
