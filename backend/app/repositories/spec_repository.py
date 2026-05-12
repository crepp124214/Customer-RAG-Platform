from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.product_spec import ProductSpec


class SpecRepository:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def get_by_id(self, spec_id: str) -> ProductSpec | None:
        return self.db_session.get(ProductSpec, spec_id)

    def add(self, spec: ProductSpec) -> ProductSpec:
        self.db_session.add(spec)
        self.db_session.flush()
        return spec

    def add_batch(self, specs: list[ProductSpec]) -> list[ProductSpec]:
        self.db_session.add_all(specs)
        self.db_session.flush()
        return specs

    def list_by_product(
        self,
        product_id: str,
        *,
        spec_category: str | None = None,
    ) -> list[ProductSpec]:
        statement = select(ProductSpec).where(ProductSpec.product_id == product_id)

        if spec_category:
            statement = statement.where(ProductSpec.spec_category == spec_category)

        return list(self.db_session.scalars(statement).all())

    def delete_by_product(self, product_id: str) -> int:
        specs = self.list_by_product(product_id)
        count = len(specs)
        for spec in specs:
            self.db_session.delete(spec)
        return count
