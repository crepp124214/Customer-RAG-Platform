from __future__ import annotations

from pydantic import BaseModel


class UploadDocumentData(BaseModel):
    document_id: str
    task_id: str


class DocumentDetailData(BaseModel):
    id: str
    name: str
    file_type: str
    status: str
    storage_path: str
    created_at: str
    updated_at: str


class TaskDetailData(BaseModel):
    id: str
    document_id: str
    task_type: str
    status: str
    error_message: str | None
    created_at: str
    updated_at: str


class BatchDeleteDocumentsRequest(BaseModel):
    document_ids: list[str]


class DocumentPreviewChunk(BaseModel):
    chunk_index: int
    content: str
    source_type: str | None
    page_number: int | None
