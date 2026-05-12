import { defineStore } from "pinia"

import {
  fetchProducts,
  fetchProduct,
  createProduct,
  updateProduct,
  deleteProduct,
} from "@/services/products"
import type { Product, ProductForm } from "@/types/product"

interface ProductState {
  items: Product[]
  currentProduct: Product | null
  isLoading: boolean
  error: string | null
}

export const useProductStore = defineStore("products", {
  state: (): ProductState => ({
    items: [],
    currentProduct: null,
    isLoading: false,
    error: null,
  }),

  getters: {
    productCount(state): number {
      return state.items.length
    },
    activeProducts(state): Product[] {
      return state.items.filter((product) => product.status === "active")
    },
  },

  actions: {
    async fetchProducts() {
      this.isLoading = true
      this.error = null

      try {
        this.items = await fetchProducts()
      } catch (error) {
        this.error = error instanceof Error ? error.message : "加载产品列表失败。"
      } finally {
        this.isLoading = false
      }
    },

    async fetchProduct(productId: string) {
      this.isLoading = true
      this.error = null

      try {
        this.currentProduct = await fetchProduct(productId)
      } catch (error) {
        this.error = error instanceof Error ? error.message : "加载产品详情失败。"
      } finally {
        this.isLoading = false
      }
    },

    async createProduct(form: ProductForm) {
      this.error = null

      try {
        const product = await createProduct(form)
        this.items.unshift(product)
        return product
      } catch (error) {
        this.error = error instanceof Error ? error.message : "创建产品失败。"
        throw error
      }
    },

    async updateProduct(productId: string, form: ProductForm) {
      this.error = null

      try {
        const updated = await updateProduct(productId, form)
        const index = this.items.findIndex((item) => item.id === productId)
        if (index >= 0) {
          this.items.splice(index, 1, updated)
        }
        if (this.currentProduct?.id === productId) {
          this.currentProduct = updated
        }
        return updated
      } catch (error) {
        this.error = error instanceof Error ? error.message : "更新产品失败。"
        throw error
      }
    },

    async deleteProduct(productId: string) {
      this.error = null

      try {
        await deleteProduct(productId)
        this.items = this.items.filter((item) => item.id !== productId)
        if (this.currentProduct?.id === productId) {
          this.currentProduct = null
        }
      } catch (error) {
        this.error = error instanceof Error ? error.message : "删除产品失败。"
        throw error
      }
    },
  },
})
