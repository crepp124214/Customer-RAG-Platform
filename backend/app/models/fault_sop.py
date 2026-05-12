from __future__ import annotations

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, TimestampMixin, generate_id


class FaultSOP(TimestampMixin, Base):
    __tablename__ = "fault_sops"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    fault_type: Mapped[str] = mapped_column(String(255), nullable=False)
    fault_category: Mapped[str] = mapped_column(String(100), nullable=False)
    symptoms: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    steps: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    resolution: Mapped[str] = mapped_column(Text, nullable=False, default="")

    product = relationship("Product", back_populates="fault_sops")
