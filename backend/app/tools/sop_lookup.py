from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from backend.app.exceptions import AppError
from backend.app.models.fault_sop import FaultSOP
from backend.app.models.product import Product
from backend.app.tools.base import ToolCallRecord, ToolDefinition, ToolExecutionResult


class SOPLookupTool:
    @classmethod
    def definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name="sop_lookup",
            description="查询故障排查SOP",
            parameters={
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "产品名称",
                    },
                    "fault_type": {
                        "type": "string",
                        "description": "故障类型",
                    },
                },
                "required": ["product_name", "fault_type"],
            },
            handler=cls.execute,
        )

    @staticmethod
    def execute(db_session: Session | None, arguments: dict[str, Any]) -> ToolExecutionResult:
        if db_session is None:
            raise AppError("数据库会话不可用", code="TOOL_EXECUTION_ERROR", status_code=500)

        product_name = arguments.get("product_name", "")
        fault_type = arguments.get("fault_type", "")

        product = db_session.query(Product).filter(Product.name == product_name).first()
        if product is None:
            return ToolExecutionResult(
                output={"sops": [], "message": f"未找到产品：{product_name}"},
                record=ToolCallRecord(
                    tool_name="sop_lookup",
                    arguments=arguments,
                    status="success",
                    result_summary=f"未找到产品：{product_name}",
                ),
            )

        sops = (
            db_session.query(FaultSOP)
            .filter(FaultSOP.product_id == product.id, FaultSOP.fault_type == fault_type)
            .all()
        )

        sop_list = [
            {
                "fault_type": sop.fault_type,
                "fault_category": sop.fault_category,
                "symptoms": sop.symptoms,
                "steps": sop.steps,
                "resolution": sop.resolution,
            }
            for sop in sops
        ]

        return ToolExecutionResult(
            output={"sops": sop_list, "product_name": product_name, "fault_type": fault_type},
            record=ToolCallRecord(
                tool_name="sop_lookup",
                arguments=arguments,
                status="success",
                result_summary=f"找到 {len(sop_list)} 条SOP记录",
            ),
        )
