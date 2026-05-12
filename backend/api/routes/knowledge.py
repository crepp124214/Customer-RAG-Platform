from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.api.deps.database import get_db_session
from backend.api.schemas.knowledge import (
    ManualData,
    ManualUploadRequest,
    SOPCreateRequest,
    SOPData,
    SpecData,
    SpecImportRequest,
)
from backend.api.schemas.response import success_response

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/manuals")
def upload_manual(
    payload: ManualUploadRequest,
    db_session: Session = Depends(get_db_session),
) -> dict:
    return success_response(
        message="手册上传成功",
        data=ManualData(
            id="placeholder",
            product_id=payload.product_id,
            title=payload.title,
            file_type=payload.file_type,
            status="pending",
            created_at="",
            updated_at="",
        ).model_dump(),
    )


@router.get("/manuals")
def list_manuals(
    product_id: str = Query(...),
    db_session: Session = Depends(get_db_session),
) -> dict:
    return success_response(message="获取手册列表成功", data=[])


@router.post("/specs")
def import_specs(
    payload: SpecImportRequest,
    db_session: Session = Depends(get_db_session),
) -> dict:
    return success_response(
        message="规格导入成功",
        data=[
            SpecData(
                id="placeholder",
                product_id=payload.product_id,
                spec_name=spec.spec_name,
                spec_value=spec.spec_value,
                spec_category=spec.spec_category,
            ).model_dump()
            for spec in payload.specs
        ],
    )


@router.get("/specs")
def list_specs(
    product_id: str = Query(...),
    db_session: Session = Depends(get_db_session),
) -> dict:
    return success_response(message="获取规格列表成功", data=[])


@router.post("/sops")
def create_sop(
    payload: SOPCreateRequest,
    db_session: Session = Depends(get_db_session),
) -> dict:
    return success_response(
        message="SOP创建成功",
        data=SOPData(
            id="placeholder",
            product_id=payload.product_id,
            fault_type=payload.fault_type,
            fault_category=payload.fault_category,
            symptoms=payload.symptoms,
            steps=payload.steps,
            resolution=payload.resolution,
        ).model_dump(),
    )


@router.get("/sops")
def list_sops(
    product_id: str = Query(...),
    db_session: Session = Depends(get_db_session),
) -> dict:
    return success_response(message="获取SOP列表成功", data=[])
