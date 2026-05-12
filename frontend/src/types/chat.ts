export interface ChatSession {
  id: string
  title: string | null
  product_id: string | null
  ticket_id: string | null
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id: string
  session_id: string
  role: 'user' | 'assistant'
  content: string
  citations: Citation[]
  tool_calls: ToolCall[]
  created_at: string
  updated_at: string
}

export interface Citation {
  document_id: string
  document_name: string
  chunk_id: string
  content: string
  page_number: number | null
  source_type: string
  asset_label: string | null
  preview_available: boolean
}

export interface ToolCall {
  tool_name: string
  arguments: Record<string, unknown>
  status: string
  result_summary: string | null
  error_code: string | null
  error_detail: string | null
}

export interface CreateSessionResult {
  session_id: string
  title: string
}
