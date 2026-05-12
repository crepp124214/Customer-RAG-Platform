import { defineStore } from "pinia"

import {
  fetchManuals,
  uploadManual,
  fetchSpecs,
  importSpecs,
  fetchSOPs,
  createSOP,
  type UploadManualPayload,
  type ImportSpecsPayload,
  type CreateSOPPayload,
} from "@/services/knowledge"
import type { ProductManual, ProductSpec, FaultSOP } from "@/types/knowledge"

interface KnowledgeState {
  manuals: ProductManual[]
  specs: ProductSpec[]
  sops: FaultSOP[]
  isLoading: boolean
  error: string | null
}

export const useKnowledgeStore = defineStore("knowledge", {
  state: (): KnowledgeState => ({
    manuals: [],
    specs: [],
    sops: [],
    isLoading: false,
    error: null,
  }),

  getters: {
    manualCount(state): number {
      return state.manuals.length
    },
    specCount(state): number {
      return state.specs.length
    },
    sopCount(state): number {
      return state.sops.length
    },
  },

  actions: {
    async fetchManuals(productId: string) {
      this.isLoading = true
      this.error = null

      try {
        this.manuals = await fetchManuals(productId)
      } catch (error) {
        this.error = error instanceof Error ? error.message : "加载手册列表失败。"
      } finally {
        this.isLoading = false
      }
    },

    async uploadManual(file: File, payload: UploadManualPayload) {
      this.error = null

      try {
        const manual = await uploadManual(file, payload)
        this.manuals.unshift(manual)
        return manual
      } catch (error) {
        this.error = error instanceof Error ? error.message : "上传手册失败。"
        throw error
      }
    },

    async fetchSpecs(productId: string) {
      this.isLoading = true
      this.error = null

      try {
        this.specs = await fetchSpecs(productId)
      } catch (error) {
        this.error = error instanceof Error ? error.message : "加载规格列表失败。"
      } finally {
        this.isLoading = false
      }
    },

    async importSpecs(payload: ImportSpecsPayload) {
      this.error = null

      try {
        const spec = await importSpecs(payload)
        this.specs.unshift(spec)
        return spec
      } catch (error) {
        this.error = error instanceof Error ? error.message : "导入规格失败。"
        throw error
      }
    },

    async fetchSOPs(productId: string) {
      this.isLoading = true
      this.error = null

      try {
        this.sops = await fetchSOPs(productId)
      } catch (error) {
        this.error = error instanceof Error ? error.message : "加载SOP列表失败。"
      } finally {
        this.isLoading = false
      }
    },

    async createSOP(payload: CreateSOPPayload) {
      this.error = null

      try {
        const sop = await createSOP(payload)
        this.sops.unshift(sop)
        return sop
      } catch (error) {
        this.error = error instanceof Error ? error.message : "创建SOP失败。"
        throw error
      }
    },
  },
})
