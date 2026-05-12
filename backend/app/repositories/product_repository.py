from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from backend.app.models.product import Product


class ProductRepository:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def get_by_id(self, product_id: str) -> Product | None:
        return self.db_session.get(Product, product_id)

    def add(self, product: Product) -> Product:
        self.db_session.add(product)
        self.db_session.flush()
        return product

    def list_products(
        self,
        *,
        search: str | None = None,
        category: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Product]:
        statement = select(Product)

        if search:
            statement = statement.where(Product.name.ilike(f"%{search}%"))

        if category:
            statement = statement.where(Product.category == category)

        sort_column = getattr(Product, sort_by, Product.created_at)
        if order == "asc":
            statement = statement.order_by(sort_column.asc())
        else:
            statement = statement.order_by(sort_column.desc())

        statement = statement.offset(offset)
        if limit:
            statement = statement.limit(limit)

        return list(self.db_session.scalars(statement).all())

    def count_products(
        self,
        *,
        search: str | None = None,
        category: str | None = None,
    ) -> int:
        statement = select(func.count(Product.id))

        if search:
            statement = statement.where(Product.name.ilike(f"%{search}%"))

        if category:
            statement = statement.where(Product.category == category)

        return int(self.db_session.scalar(statement) or 0)

    def update(self, product_id: str, **kwargs) -> Product | None:
        product = self.get_by_id(product_id)
        if product is None:
            return None
        for key, value in kwargs.items():
            setattr(product, key, value)
        self.db_session.flush()
        return product

    def delete(self, product_id: str) -> bool:
        product = self.get_by_id(product_id)
        if product is None:
            return False
        self.db_session.delete(product)
        return True
