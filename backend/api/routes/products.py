from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.api.deps.database import get_db_session
from backend.api.schemas.products import (
    ProductCreateRequest,
    ProductData,
    ProductListData,
    ProductUpdateRequest,
)
from backend.api.schemas.response import success_response

router = APIRouter(prefix="/products", tags=["products"])


@router.post("")
def create_product(
    payload: ProductCreateRequest,
    db_session: Session = Depends(get_db_session),
) -> dict:
    return success_response(
        message="产品创建成功",
        data=ProductData(
            id="placeholder",
            name=payload.name,
            category=payload.category,
            version=payload.version,
            status="active",
            created_at="",
            updated_at="",
        ).model_dump(),
    )


@router.get("")
def list_products(
    category: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db_session: Session = Depends(get_db_session),
) -> dict:
    return success_response(
        message="获取产品列表成功",
        data=ProductListData(items=[], total=0).model_dump(),
    )


@router.get("/{product_id}")
def get_product(
    product_id: str,
    db_session: Session = Depends(get_db_session),
) -> dict:
    return success_response(
        message="获取产品详情成功",
        data=ProductData(
            id=product_id,
            name="",
            category="",
            version="",
            status="",
            created_at="",
            updated_at="",
        ).model_dump(),
    )


@router.put("/{product_id}")
def update_product(
    product_id: str,
    payload: ProductUpdateRequest,
    db_session: Session = Depends(get_db_session),
) -> dict:
    return success_response(
        message="产品更新成功",
        data=ProductData(
            id=product_id,
            name=payload.name or "",
            category=payload.category or "",
            version=payload.version or "",
            status=payload.status or "",
            created_at="",
            updated_at="",
        ).model_dump(),
    )


@router.delete("/{product_id}")
def delete_product(
    product_id: str,
    db_session: Session = Depends(get_db_session),
) -> dict:
    return success_response(message="产品删除成功")
