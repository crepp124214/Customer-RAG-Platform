from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.exceptions import AppError
from backend.app.models.product import Product
from backend.app.repositories.product_repository import ProductRepository


class ProductService:
    def __init__(self) -> None:
        pass

    def create_product(
        self,
        db_session: Session,
        *,
        name: str,
        category: str,
        version: str = "1.0",
    ) -> Product:
        repository = ProductRepository(db_session)

        existing = db_session.scalar(
            select(Product).where(Product.name == name, Product.version == version)
        )
        if existing is not None:
            raise AppError(
                f"产品已存在: {name} v{version}",
                code="product_already_exists",
                status_code=409,
            )

        product = Product(name=name, category=category, version=version)
        return repository.add(product)

    def get_product(self, db_session: Session, *, product_id: str) -> Product:
        repository = ProductRepository(db_session)
        product = repository.get_by_id(product_id)
        if product is None:
            raise AppError("产品不存在", code="product_not_found", status_code=404)
        return product

    def list_products(
        self,
        db_session: Session,
        *,
        search: str | None = None,
        category: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Product]:
        repository = ProductRepository(db_session)
        return repository.list_products(
            search=search,
            category=category,
            sort_by=sort_by,
            order=order,
            limit=limit,
            offset=offset,
        )

    def update_product(
        self,
        db_session: Session,
        *,
        product_id: str,
        name: str | None = None,
        category: str | None = None,
        version: str | None = None,
        status: str | None = None,
    ) -> Product:
        repository = ProductRepository(db_session)
        product = repository.get_by_id(product_id)
        if product is None:
            raise AppError("产品不存在", code="product_not_found", status_code=404)

        updates: dict = {}
        if name is not None:
            updates["name"] = name
        if category is not None:
            updates["category"] = category
        if version is not None:
            updates["version"] = version
        if status is not None:
            updates["status"] = status

        if updates:
            repository.update(product_id, **updates)
            db_session.refresh(product)

        return product

    def delete_product(self, db_session: Session, *, product_id: str) -> None:
        repository = ProductRepository(db_session)
        deleted = repository.delete(product_id)
        if not deleted:
            raise AppError("产品不存在", code="product_not_found", status_code=404)
