from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from backend.app.exceptions import AppError
from backend.app.models.product import Product
from backend.app.models.ticket import Ticket
from backend.app.tools.base import ToolCallRecord, ToolDefinition, ToolExecutionResult


class TicketSearchTool:
    @classmethod
    def definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name="ticket_search",
            description="搜索相似历史工单",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词",
                    },
                    "product_name": {
                        "type": "string",
                        "description": "产品名称（可选，用于缩小范围）",
                    },
                },
                "required": ["query"],
            },
            handler=cls.execute,
        )

    @staticmethod
    def execute(db_session: Session | None, arguments: dict[str, Any]) -> ToolExecutionResult:
        if db_session is None:
            raise AppError("数据库会话不可用", code="TOOL_EXECUTION_ERROR", status_code=500)

        query_text = arguments.get("query", "")
        product_name = arguments.get("product_name")

        base_query = db_session.query(Ticket)

        if product_name:
            product = db_session.query(Product).filter(Product.name == product_name).first()
            if product is None:
                return ToolExecutionResult(
                    output={"tickets": [], "message": f"未找到产品：{product_name}"},
                    record=ToolCallRecord(
                        tool_name="ticket_search",
                        arguments=arguments,
                        status="success",
                        result_summary=f"未找到产品：{product_name}",
                    ),
                )
            base_query = base_query.filter(Ticket.product_id == product.id)

        search_filter = Ticket.title.ilike(f"%{query_text}%") | Ticket.description.ilike(f"%{query_text}%")
        tickets = base_query.filter(search_filter).order_by(Ticket.created_at.desc()).limit(10).all()

        ticket_list = [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "fault_category": t.fault_category,
                "priority": t.priority,
                "status": t.status,
                "solution": t.solution,
            }
            for t in tickets
        ]

        return ToolExecutionResult(
            output={"tickets": ticket_list, "query": query_text},
            record=ToolCallRecord(
                tool_name="ticket_search",
                arguments=arguments,
                status="success",
                result_summary=f"找到 {len(ticket_list)} 条相似工单",
            ),
        )
