import { requestJson } from "@/services/http"
import type { Ticket, SimilarTicket } from "@/types/ticket"

export interface CreateTicketPayload {
  product_id: string | null
  title: string
  description: string
  fault_category: string
  priority: Ticket["priority"]
}

export interface UpdateTicketStatusPayload {
  status: Ticket["status"]
}

export interface SearchSimilarParams {
  query: string
  product_id?: string
  limit?: number
}

export async function fetchTickets(productId?: string): Promise<Ticket[]> {
  const queryParams = new URLSearchParams()

  if (productId) {
    queryParams.append("product_id", productId)
  }

  const path = `/api/tickets${queryParams.toString() ? `?${queryParams.toString()}` : ""}`
  const response = await requestJson<Ticket[]>(path)

  if (!response.data) {
    throw new Error("服务未返回工单列表。")
  }

  return response.data
}

export async function fetchTicket(ticketId: string): Promise<Ticket> {
  const response = await requestJson<Ticket>(`/api/tickets/${ticketId}`)

  if (!response.data) {
    throw new Error("服务未返回工单详情。")
  }

  return response.data
}

export async function createTicket(payload: CreateTicketPayload): Promise<Ticket> {
  const response = await requestJson<Ticket>("/api/tickets", {
    method: "POST",
    body: JSON.stringify(payload),
  })

  if (!response.data) {
    throw new Error("创建工单成功，但服务未返回工单信息。")
  }

  return response.data
}

export async function updateTicketStatus(
  ticketId: string,
  payload: UpdateTicketStatusPayload,
): Promise<Ticket> {
  const response = await requestJson<Ticket>(`/api/tickets/${ticketId}/status`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  })

  if (!response.data) {
    throw new Error("更新工单状态成功，但服务未返回工单信息。")
  }

  return response.data
}

export async function searchSimilar(
  params: SearchSimilarParams,
): Promise<SimilarTicket[]> {
  const queryParams = new URLSearchParams()
  queryParams.append("query", params.query)

  if (params.product_id) {
    queryParams.append("product_id", params.product_id)
  }

  if (params.limit) {
    queryParams.append("limit", params.limit.toString())
  }

  const response = await requestJson<SimilarTicket[]>(
    `/api/tickets/similar?${queryParams.toString()}`,
  )

  if (!response.data) {
    throw new Error("服务未返回相似工单。")
  }

  return response.data
}
