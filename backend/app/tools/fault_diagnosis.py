from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from backend.app.exceptions import AppError
from backend.app.models.fault_sop import FaultSOP
from backend.app.models.product import Product
from backend.app.tools.base import ToolCallRecord, ToolDefinition, ToolExecutionResult


class FaultDiagnosisTool:
    @classmethod
    def definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name="fault_diagnosis",
            description="启动故障诊断流程",
            parameters={
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "产品名称",
                    },
                    "symptoms": {
                        "type": "string",
                        "description": "故障症状描述",
                    },
                },
                "required": ["product_name", "symptoms"],
            },
            handler=cls.execute,
        )

    @staticmethod
    def execute(db_session: Session | None, arguments: dict[str, Any]) -> ToolExecutionResult:
        if db_session is None:
            raise AppError("数据库会话不可用", code="TOOL_EXECUTION_ERROR", status_code=500)

        product_name = arguments.get("product_name", "")
        symptoms = arguments.get("symptoms", "")

        product = db_session.query(Product).filter(Product.name == product_name).first()
        if product is None:
            return ToolExecutionResult(
                output={"diagnosis": None, "message": f"未找到产品：{product_name}"},
                record=ToolCallRecord(
                    tool_name="fault_diagnosis",
                    arguments=arguments,
                    status="success",
                    result_summary=f"未找到产品：{product_name}",
                ),
            )

        sops = (
            db_session.query(FaultSOP)
            .filter(FaultSOP.product_id == product.id)
            .all()
        )

        matched_sops = []
        for sop in sops:
            symptom_texts = [s.get("description", "") for s in (sop.symptoms or []) if isinstance(s, dict)]
            symptom_blob = " ".join(symptom_texts)
            if symptoms.lower() in symptom_blob.lower() or any(
                kw in symptom_blob.lower() for kw in symptoms.lower().split()
            ):
                matched_sops.append(sop)

        diagnosis_results = [
            {
                "fault_type": sop.fault_type,
                "fault_category": sop.fault_category,
                "symptoms": sop.symptoms,
                "steps": sop.steps,
                "resolution": sop.resolution,
            }
            for sop in matched_sops
        ]

        return ToolExecutionResult(
            output={
                "diagnosis": diagnosis_results,
                "product_name": product_name,
                "symptoms": symptoms,
            },
            record=ToolCallRecord(
                tool_name="fault_diagnosis",
                arguments=arguments,
                status="success",
                result_summary=f"匹配到 {len(matched_sops)} 条故障诊断记录",
            ),
        )
