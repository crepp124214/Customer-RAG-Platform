from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, TimestampMixin, generate_id


class ProductSpec(TimestampMixin, Base):
    __tablename__ = "product_specs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    spec_name: Mapped[str] = mapped_column(String(255), nullable=False)
    spec_value: Mapped[str] = mapped_column(String(500), nullable=False)
    spec_category: Mapped[str] = mapped_column(String(100), nullable=False)

    product = relationship("Product", back_populates="specs")
