from __future__ import annotations

from pydantic import BaseModel


class TicketCreateRequest(BaseModel):
    product_id: str | None = None
    title: str
    description: str
    fault_category: str | None = None
    priority: str | None = None


class TicketUpdateStatusRequest(BaseModel):
    status: str
    solution: str | None = None
    resolution_notes: str | None = None


class TicketData(BaseModel):
    id: str
    product_id: str | None
    title: str
    description: str
    fault_category: str | None
    priority: str | None
    status: str
    solution: str | None
    resolution_notes: str | None
    created_at: str
    updated_at: str


class SimilarTicketData(BaseModel):
    ticket: TicketData
    similarity: float
