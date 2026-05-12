export interface Ticket {
  id: string
  product_id: string | null
  title: string
  description: string
  fault_category: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  status: 'open' | 'in_progress' | 'resolved' | 'closed'
  solution: string
  resolution_notes: string
  created_at: string
  updated_at: string
}

export interface SimilarTicket {
  ticket: Ticket
  similarity: number
}
