from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.api.deps.database import get_db_session
from backend.api.schemas.diagnosis import (
    DiagnosisAnswerRequest,
    DiagnosisData,
    DiagnosisStartRequest,
    DiagnosisStepData,
)
from backend.api.schemas.response import success_response

router = APIRouter(prefix="/diagnosis", tags=["diagnosis"])


@router.post("/start")
def start_diagnosis(
    payload: DiagnosisStartRequest,
    db_session: Session = Depends(get_db_session),
) -> dict:
    return success_response(
        message="诊断启动成功",
        data=DiagnosisData(
            diagnosis_id="placeholder",
            sop_id="placeholder",
            current_step=DiagnosisStepData(
                step_order=1,
                action="",
                expected="",
            ),
            total_steps=0,
            is_complete=False,
            resolution=None,
        ).model_dump(),
    )


@router.post("/answer")
def answer_step(
    payload: DiagnosisAnswerRequest,
    db_session: Session = Depends(get_db_session),
) -> dict:
    return success_response(
        message="诊断步骤回答成功",
        data=DiagnosisData(
            diagnosis_id=payload.diagnosis_id,
            sop_id="placeholder",
            current_step=DiagnosisStepData(
                step_order=1,
                action="",
                expected="",
            ),
            total_steps=0,
            is_complete=False,
            resolution=None,
        ).model_dump(),
    )
