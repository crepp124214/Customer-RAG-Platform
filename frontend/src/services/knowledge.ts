import { requestJson } from "@/services/http"
import type { ProductManual, ProductSpec, FaultSOP } from "@/types/knowledge"

export interface UploadManualPayload {
  product_id: string
  title: string
}

export interface ImportSpecsPayload {
  product_id: string
  source: string
}

export interface CreateSOPPayload {
  product_id: string
  fault_type: string
  fault_category: string
  symptoms: Array<{ keyword: string; weight: number }>
  steps: Array<{ order: number; action: string; expected: string; next_if_pass: number; next_if_fail: number }>
  resolution: string
}

export async function fetchManuals(productId: string): Promise<ProductManual[]> {
  const response = await requestJson<ProductManual[]>(`/api/knowledge/manuals?product_id=${productId}`)

  if (!response.data) {
    throw new Error("服务未返回手册列表。")
  }

  return response.data
}

export async function uploadManual(
  file: File,
  payload: UploadManualPayload,
): Promise<ProductManual> {
  const formData = new FormData()
  formData.append("file", file)
  formData.append("product_id", payload.product_id)
  formData.append("title", payload.title)

  const response = await requestJson<ProductManual>("/api/knowledge/manuals/upload", {
    method: "POST",
    body: formData,
  })

  if (!response.data) {
    throw new Error("上传手册成功，但服务未返回手册信息。")
  }

  return response.data
}

export async function fetchSpecs(productId: string): Promise<ProductSpec[]> {
  const response = await requestJson<ProductSpec[]>(`/api/knowledge/specs?product_id=${productId}`)

  if (!response.data) {
    throw new Error("服务未返回规格列表。")
  }

  return response.data
}

export async function importSpecs(payload: ImportSpecsPayload): Promise<ProductSpec> {
  const response = await requestJson<ProductSpec>("/api/knowledge/specs/import", {
    method: "POST",
    body: JSON.stringify(payload),
  })

  if (!response.data) {
    throw new Error("导入规格成功，但服务未返回规格信息。")
  }

  return response.data
}

export async function fetchSOPs(productId: string): Promise<FaultSOP[]> {
  const response = await requestJson<FaultSOP[]>(`/api/knowledge/sops?product_id=${productId}`)

  if (!response.data) {
    throw new Error("服务未返回SOP列表。")
  }

  return response.data
}

export async function createSOP(payload: CreateSOPPayload): Promise<FaultSOP> {
  const response = await requestJson<FaultSOP>("/api/knowledge/sops", {
    method: "POST",
    body: JSON.stringify(payload),
  })

  if (!response.data) {
    throw new Error("创建SOP成功，但服务未返回SOP信息。")
  }

  return response.data
}
