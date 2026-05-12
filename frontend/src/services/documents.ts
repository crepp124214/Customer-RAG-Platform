import { requestJson } from "@/services/http"

export interface UploadDocumentData {
  document_id: string
  task_id: string
}

export interface DocumentDetailData {
  id: string
  name: string
  file_type: string
  status: string
  storage_path: string
  created_at: string
  updated_at: string
}

export interface TaskDetailData {
  id: string
  document_id: string
  task_type: string
  status: string
  error_message: string | null
  created_at: string
  updated_at: string
}

export async function uploadDocument(file: File): Promise<UploadDocumentData> {
  const formData = new FormData()
  formData.append("file", file)

  const response = await requestJson<UploadDocumentData>("/api/documents/upload", {
    method: "POST",
    body: formData,
  })

  if (!response.data) {
    throw new Error("文档上传成功，但服务未返回文档信息。")
  }

  return response.data
}

export async function fetchDocument(documentId: string): Promise<DocumentDetailData> {
  const response = await requestJson<DocumentDetailData>(`/api/documents/${documentId}`)

  if (!response.data) {
    throw new Error("服务未返回文档详情。")
  }

  return response.data
}

export async function removeDocument(documentId: string): Promise<void> {
  await requestJson<null>(`/api/documents/${documentId}`, {
    method: "DELETE",
  })
}

export async function searchDocuments(
  search?: string,
  sort?: string,
  order?: "asc" | "desc",
): Promise<DocumentDetailData[]> {
  const queryParams = new URLSearchParams()

  if (search) {
    queryParams.append("search", search)
  }

  if (sort) {
    queryParams.append("sort", sort)
  }

  if (order) {
    queryParams.append("order", order)
  }

  const response = await requestJson<DocumentDetailData[]>(
    `/api/documents?${queryParams.toString()}`,
  )

  if (!response.data) {
    throw new Error("服务未返回文档列表。")
  }

  return response.data
}

export async function batchDeleteDocuments(documentIds: string[]): Promise<void> {
  await requestJson<null>("/api/documents/batch-delete", {
    method: "POST",
    body: JSON.stringify({ document_ids: documentIds }),
  })
}
