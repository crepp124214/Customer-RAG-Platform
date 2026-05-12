import { defineStore } from "pinia"

import {
  fetchTickets,
  fetchTicket,
  createTicket,
  updateTicketStatus,
  searchSimilar,
  type CreateTicketPayload,
  type UpdateTicketStatusPayload,
  type SearchSimilarParams,
} from "@/services/tickets"
import type { Ticket, SimilarTicket } from "@/types/ticket"

interface TicketState {
  items: Ticket[]
  currentTicket: Ticket | null
  similarTickets: SimilarTicket[]
  isLoading: boolean
  error: string | null
}

export const useTicketStore = defineStore("tickets", {
  state: (): TicketState => ({
    items: [],
    currentTicket: null,
    similarTickets: [],
    isLoading: false,
    error: null,
  }),

  getters: {
    ticketCount(state): number {
      return state.items.length
    },
    openTickets(state): Ticket[] {
      return state.items.filter((ticket) => ticket.status === "open")
    },
  },

  actions: {
    async fetchTickets(productId?: string) {
      this.isLoading = true
      this.error = null

      try {
        this.items = await fetchTickets(productId)
      } catch (error) {
        this.error = error instanceof Error ? error.message : "加载工单列表失败。"
      } finally {
        this.isLoading = false
      }
    },

    async fetchTicket(ticketId: string) {
      this.isLoading = true
      this.error = null

      try {
        this.currentTicket = await fetchTicket(ticketId)
      } catch (error) {
        this.error = error instanceof Error ? error.message : "加载工单详情失败。"
      } finally {
        this.isLoading = false
      }
    },

    async createTicket(payload: CreateTicketPayload) {
      this.error = null

      try {
        const ticket = await createTicket(payload)
        this.items.unshift(ticket)
        return ticket
      } catch (error) {
        this.error = error instanceof Error ? error.message : "创建工单失败。"
        throw error
      }
    },

    async updateTicketStatus(ticketId: string, payload: UpdateTicketStatusPayload) {
      this.error = null

      try {
        const updated = await updateTicketStatus(ticketId, payload)
        const index = this.items.findIndex((item) => item.id === ticketId)
        if (index >= 0) {
          this.items.splice(index, 1, updated)
        }
        if (this.currentTicket?.id === ticketId) {
          this.currentTicket = updated
        }
        return updated
      } catch (error) {
        this.error = error instanceof Error ? error.message : "更新工单状态失败。"
        throw error
      }
    },

    async searchSimilar(params: SearchSimilarParams) {
      this.isLoading = true
      this.error = null

      try {
        this.similarTickets = await searchSimilar(params)
        return this.similarTickets
      } catch (error) {
        this.error = error instanceof Error ? error.message : "搜索相似工单失败。"
        throw error
      } finally {
        this.isLoading = false
      }
    },
  },
})
