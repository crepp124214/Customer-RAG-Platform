import { requestJson } from "@/services/http"
import type { Product, ProductForm } from "@/types/product"

export async function fetchProducts(): Promise<Product[]> {
  const response = await requestJson<Product[]>("/api/products")

  if (!response.data) {
    throw new Error("服务未返回产品列表。")
  }

  return response.data
}

export async function fetchProduct(productId: string): Promise<Product> {
  const response = await requestJson<Product>(`/api/products/${productId}`)

  if (!response.data) {
    throw new Error("服务未返回产品详情。")
  }

  return response.data
}

export async function createProduct(form: ProductForm): Promise<Product> {
  const response = await requestJson<Product>("/api/products", {
    method: "POST",
    body: JSON.stringify(form),
  })

  if (!response.data) {
    throw new Error("创建产品成功，但服务未返回产品信息。")
  }

  return response.data
}

export async function updateProduct(productId: string, form: ProductForm): Promise<Product> {
  const response = await requestJson<Product>(`/api/products/${productId}`, {
    method: "PUT",
    body: JSON.stringify(form),
  })

  if (!response.data) {
    throw new Error("更新产品成功，但服务未返回产品信息。")
  }

  return response.data
}

export async function deleteProduct(productId: string): Promise<void> {
  await requestJson<null>(`/api/products/${productId}`, {
    method: "DELETE",
  })
}
