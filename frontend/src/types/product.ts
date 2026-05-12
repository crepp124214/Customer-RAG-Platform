export interface Product {
  id: string
  name: string
  category: string
  version: string
  status: 'active' | 'deprecated'
  created_at: string
  updated_at: string
}

export interface ProductForm {
  name: string
  category: string
  version: string
}
