from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.api.deps.database import get_db_session
from backend.api.schemas.response import success_response
from backend.api.schemas.tickets import (
    SimilarTicketData,
    TicketCreateRequest,
    TicketData,
    TicketUpdateStatusRequest,
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("")
def create_ticket(
    payload: TicketCreateRequest,
    db_session: Session = Depends(get_db_session),
) -> dict:
    return success_response(
        message="工单创建成功",
        data=TicketData(
            id="placeholder",
            product_id=payload.product_id,
            title=payload.title,
            description=payload.description,
            fault_category=payload.fault_category,
            priority=payload.priority,
            status="open",
            solution=None,
            resolution_notes=None,
            created_at="",
            updated_at="",
        ).model_dump(),
    )


@router.get("")
def list_tickets(
    status: str | None = Query(default=None),
    product_id: str | None = Query(default=None),
    db_session: Session = Depends(get_db_session),
) -> dict:
    return success_response(message="获取工单列表成功", data=[])


@router.get("/{ticket_id}")
def get_ticket(
    ticket_id: str,
    db_session: Session = Depends(get_db_session),
) -> dict:
    return success_response(
        message="获取工单详情成功",
        data=TicketData(
            id=ticket_id,
            product_id=None,
            title="",
            description="",
            fault_category=None,
            priority=None,
            status="",
            solution=None,
            resolution_notes=None,
            created_at="",
            updated_at="",
        ).model_dump(),
    )


@router.put("/{ticket_id}/status")
def update_ticket_status(
    ticket_id: str,
    payload: TicketUpdateStatusRequest,
    db_session: Session = Depends(get_db_session),
) -> dict:
    return success_response(
        message="工单状态更新成功",
        data=TicketData(
            id=ticket_id,
            product_id=None,
            title="",
            description="",
            fault_category=None,
            priority=None,
            status=payload.status,
            solution=payload.solution,
            resolution_notes=payload.resolution_notes,
            created_at="",
            updated_at="",
        ).model_dump(),
    )


@router.post("/search")
def search_similar_tickets(
    payload: dict,
    db_session: Session = Depends(get_db_session),
) -> dict:
    return success_response(message="相似工单搜索完成", data=[])
