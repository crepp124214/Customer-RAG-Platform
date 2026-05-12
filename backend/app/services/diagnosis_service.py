from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.exceptions import AppError
from backend.app.models.fault_sop import FaultSOP
from backend.app.models.message import Message
from backend.app.repositories.fault_sop_repository import FaultSOPRepository
from backend.app.repositories.message_repository import MessageRepository


class DiagnosisService:
    def __init__(self) -> None:
        pass

    def start_diagnosis(
        self,
        db_session: Session,
        *,
        product_id: str,
        symptoms: list[str],
    ) -> dict:
        sop = self.get_sop_by_symptoms(db_session, product_id=product_id, symptoms=symptoms)
        if sop is None:
            raise AppError(
                "未找到匹配的故障诊断流程",
                code="sop_not_found",
                status_code=404,
            )

        steps = sop.steps or []
        if not steps:
            raise AppError(
                "诊断流程无有效步骤",
                code="sop_empty_steps",
                status_code=400,
            )

        first_step = steps[0]
        diagnosis_context = {
            "sop_id": sop.id,
            "current_step_index": 0,
            "total_steps": len(steps),
            "product_id": product_id,
            "symptoms": symptoms,
        }

        return {
            "sop_id": sop.id,
            "current_step": first_step,
            "current_step_index": 0,
            "total_steps": len(steps),
            "diagnosis_context": diagnosis_context,
        }

    def answer_step(
        self,
        db_session: Session,
        *,
        diagnosis_id: str,
        passed: bool,
    ) -> dict:
        message_repository = MessageRepository(db_session)
        message = message_repository.list_by_session_id(diagnosis_id)
        diagnosis_message = None
        for msg in reversed(message):
            if msg.diagnosis_context is not None:
                diagnosis_message = msg
                break

        if diagnosis_message is None:
            raise AppError(
                "未找到诊断上下文",
                code="diagnosis_context_not_found",
                status_code=404,
            )

        context = diagnosis_message.diagnosis_context
        sop_id = context.get("sop_id")
        current_step_index = context.get("current_step_index", 0)

        sop_repository = FaultSOPRepository(db_session)
        sop = sop_repository.get_by_id(sop_id)
        if sop is None:
            raise AppError("诊断流程不存在", code="sop_not_found", status_code=404)

        steps = sop.steps or []
        if current_step_index >= len(steps):
            raise AppError(
                "诊断步骤索引越界",
                code="step_index_out_of_range",
                status_code=400,
            )

        current_step = steps[current_step_index]
        next_step_key = "next_if_pass" if passed else "next_if_fail"
        next_step_index = current_step.get(next_step_key)

        if next_step_index is None or (isinstance(next_step_index, int) and next_step_index >= len(steps)):
            resolution = current_step.get("resolution", sop.resolution)
            updated_context = {
                **context,
                "current_step_index": current_step_index,
                "is_complete": True,
                "last_passed": passed,
            }
            return {
                "next_step": None,
                "is_complete": True,
                "resolution": resolution,
                "diagnosis_context": updated_context,
            }

        next_step = steps[next_step_index]
        updated_context = {
            **context,
            "current_step_index": next_step_index,
            "is_complete": False,
            "last_passed": passed,
        }

        return {
            "next_step": next_step,
            "is_complete": False,
            "resolution": None,
            "diagnosis_context": updated_context,
        }

    def get_sop_by_symptoms(
        self,
        db_session: Session,
        *,
        product_id: str,
        symptoms: list[str],
    ) -> FaultSOP | None:
        sop_repository = FaultSOPRepository(db_session)
        matched_sops = sop_repository.find_by_product_and_symptoms(product_id, symptoms)
        if not matched_sops:
            return None
        return matched_sops[0]
