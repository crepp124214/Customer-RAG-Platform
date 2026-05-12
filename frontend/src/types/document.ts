export interface Document {
  id: string
  name: string
  file_type: string
  status: string
  storage_path: string
  created_at: string
  updated_at: string
}

export interface DocumentSearchParams {
  search?: string
  sort?: string
  order?: 'asc' | 'desc'
}

export interface BatchDeleteParams {
  document_ids: string[]
}

export interface UploadResult {
  document_id: string
  task_id: string
}

export interface Task {
  id: string
  document_id: string
  task_type: string
  status: string
  error_message: string | null
  created_at: string
  updated_at: string
}
