from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from backend.app.exceptions import AppError
from backend.app.models.product import Product
from backend.app.models.product_spec import ProductSpec
from backend.app.tools.base import ToolCallRecord, ToolDefinition, ToolExecutionResult


class ProductSpecLookupTool:
    @classmethod
    def definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name="product_spec_lookup",
            description="查询产品参数/规格",
            parameters={
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "产品名称",
                    },
                    "spec_name": {
                        "type": "string",
                        "description": "规格名称（可选，不传则返回全部规格）",
                    },
                },
                "required": ["product_name"],
            },
            handler=cls.execute,
        )

    @staticmethod
    def execute(db_session: Session | None, arguments: dict[str, Any]) -> ToolExecutionResult:
        if db_session is None:
            raise AppError("数据库会话不可用", code="TOOL_EXECUTION_ERROR", status_code=500)

        product_name = arguments.get("product_name", "")
        spec_name = arguments.get("spec_name")

        product = db_session.query(Product).filter(Product.name == product_name).first()
        if product is None:
            return ToolExecutionResult(
                output={"specs": [], "message": f"未找到产品：{product_name}"},
                record=ToolCallRecord(
                    tool_name="product_spec_lookup",
                    arguments=arguments,
                    status="success",
                    result_summary=f"未找到产品：{product_name}",
                ),
            )

        query = db_session.query(ProductSpec).filter(ProductSpec.product_id == product.id)
        if spec_name:
            query = query.filter(ProductSpec.spec_name == spec_name)

        specs = query.all()
        spec_list = [
            {
                "spec_name": s.spec_name,
                "spec_value": s.spec_value,
                "spec_category": s.spec_category,
            }
            for s in specs
        ]

        return ToolExecutionResult(
            output={"specs": spec_list, "product_name": product_name},
            record=ToolCallRecord(
                tool_name="product_spec_lookup",
                arguments=arguments,
                status="success",
                result_summary=f"找到 {len(spec_list)} 条规格记录",
            ),
        )
