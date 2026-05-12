from __future__ import annotations

from pydantic import BaseModel


class DiagnosisStartRequest(BaseModel):
    product_id: str
    symptoms: list[str]


class DiagnosisAnswerRequest(BaseModel):
    diagnosis_id: str
    passed: bool


class DiagnosisStepData(BaseModel):
    step_order: int
    action: str
    expected: str


class DiagnosisData(BaseModel):
    diagnosis_id: str
    sop_id: str
    current_step: DiagnosisStepData
    total_steps: int
    is_complete: bool
    resolution: str | None = None
