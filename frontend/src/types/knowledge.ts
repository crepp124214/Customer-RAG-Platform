export interface ProductManual {
  id: string
  product_id: string
  title: string
  file_type: string
  status: string
  created_at: string
  updated_at: string
}

export interface ProductSpec {
  id: string
  product_id: string
  spec_name: string
  spec_value: string
  spec_category: string
}

export interface FaultSOP {
  id: string
  product_id: string
  fault_type: string
  fault_category: string
  symptoms: Array<{ keyword: string; weight: number }>
  steps: Array<{ order: number; action: string; expected: string; next_if_pass: number; next_if_fail: number }>
  resolution: string
}
