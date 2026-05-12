from __future__ import annotations

from pydantic import BaseModel


class ProductCreateRequest(BaseModel):
    name: str
    category: str
    version: str


class ProductUpdateRequest(BaseModel):
    name: str | None = None
    category: str | None = None
    version: str | None = None
    status: str | None = None


class ProductData(BaseModel):
    id: str
    name: str
    category: str
    version: str
    status: str
    created_at: str
    updated_at: str


class ProductListData(BaseModel):
    items: list[ProductData]
    total: int
