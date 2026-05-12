from __future__ import annotations

from pydantic import BaseModel


class ManualUploadRequest(BaseModel):
    product_id: str
    title: str
    file_type: str


class ManualData(BaseModel):
    id: str
    product_id: str
    title: str
    file_type: str
    status: str
    created_at: str
    updated_at: str


class SpecItem(BaseModel):
    spec_name: str
    spec_value: str
    spec_category: str


class SpecImportRequest(BaseModel):
    product_id: str
    specs: list[SpecItem]


class SpecData(BaseModel):
    id: str
    product_id: str
    spec_name: str
    spec_value: str
    spec_category: str


class SOPCreateRequest(BaseModel):
    product_id: str
    fault_type: str
    fault_category: str
    symptoms: list[str]
    steps: list[str]
    resolution: str


class SOPData(BaseModel):
    id: str
    product_id: str
    fault_type: str
    fault_category: str
    symptoms: list[str]
    steps: list[str]
    resolution: str
