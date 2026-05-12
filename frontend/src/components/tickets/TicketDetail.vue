<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue"

import { useTicketStore } from "@/stores/tickets"
import type { Ticket } from "@/types/ticket"
import StatusBadge from "@/components/common/StatusBadge.vue"

const props = defineProps<{
  ticketId: string
}>()

const ticketStore = useTicketStore()

const ticket = computed(() => ticketStore.currentTicket)
const similarTickets = computed(() => ticketStore.similarTickets)

const showSimilarPanel = ref(false)

const priorityLabel: Record<string, string> = {
  low: "低",
  medium: "中",
  high: "高",
  urgent: "紧急",
}

const priorityType: Record<string, string> = {
  low: "info",
  medium: "warning",
  high: "danger",
  urgent: "danger",
}

const nextStatusMap: Record<string, Ticket["status"] | null> = {
  open: "in_progress",
  in_progress: "resolved",
  resolved: "closed",
  closed: null,
}

const nextStatusLabel: Record<string, string> = {
  open: "开始处理",
  in_progress: "标记已解决",
  resolved: "关闭工单",
}

const nextStatus = computed(() => {
  if (!ticket.value) return null
  return nextStatusMap[ticket.value.status]
})

async function handleStatusUpdate() {
  if (!ticket.value || !nextStatus.value) return
  await ticketStore.updateTicketStatus(ticket.value.id, { status: nextStatus.value })
}

async function loadSimilarTickets() {
  if (!ticket.value) return
  await ticketStore.searchSimilar({
    query: ticket.value.description,
    product_id: ticket.value.product_id ?? undefined,
    limit: 5,
  })
  showSimilarPanel.value = true
}

function formatSimilarity(score: number): string {
  return `${(score * 100).toFixed(1)}%`
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("zh-CN")
}

async function loadTicketData() {
  await ticketStore.fetchTicket(props.ticketId)
  ticketStore.similarTickets = []
  showSimilarPanel.value = false
}

watch(() => props.ticketId, () => {
  void loadTicketData()
})

onMounted(() => {
  void loadTicketData()
})
</script>

<template>
  <section class="ticket-detail-panel">
    <el-alert
      v-if="ticketStore.error"
      :closable="false"
      type="error"
      show-icon
      title="加载失败"
      :description="ticketStore.error"
    />

    <div v-if="ticketStore.isLoading" v-loading="true" class="loading-placeholder" />

    <template v-if="ticket">
      <header class="detail-header">
        <div class="detail-title-area">
          <span class="detail-eyebrow">工单详情</span>
          <h2>{{ ticket.title }}</h2>
          <div class="detail-meta">
            <StatusBadge :status="ticket.status" type="ticket" />
            <el-tag :type="priorityType[ticket.priority]" size="small" effect="plain">
              {{ priorityLabel[ticket.priority] }}
            </el-tag>
            <span v-if="ticket.fault_category" class="meta-category">{{ ticket.fault_category }}</span>
          </div>
        </div>
        <div class="detail-actions">
          <el-button
            v-if="nextStatus"
            type="primary"
            @click="handleStatusUpdate"
          >
            {{ nextStatusLabel[ticket.status] }}
          </el-button>
          <el-button
            :disabled="!ticket.description"
            @click="loadSimilarTickets"
          >
            查找相似工单
          </el-button>
        </div>
      </header>

      <div class="detail-body">
        <div class="detail-section">
          <h3>问题描述</h3>
          <p class="description-text">{{ ticket.description || "暂无描述" }}</p>
        </div>

        <div class="detail-grid">
          <div class="detail-item">
            <span>工单编号</span>
            <strong>{{ ticket.id }}</strong>
          </div>
          <div class="detail-item">
            <span>故障分类</span>
            <strong>{{ ticket.fault_category || "未分类" }}</strong>
          </div>
          <div class="detail-item">
            <span>创建时间</span>
            <strong>{{ formatDate(ticket.created_at) }}</strong>
          </div>
          <div class="detail-item">
            <span>更新时间</span>
            <strong>{{ formatDate(ticket.updated_at) }}</strong>
          </div>
        </div>

        <div v-if="ticket.solution" class="detail-section">
          <h3>解决方案</h3>
          <p class="description-text">{{ ticket.solution }}</p>
        </div>

        <div v-if="ticket.resolution_notes" class="detail-section">
          <h3>处理备注</h3>
          <p class="description-text">{{ ticket.resolution_notes }}</p>
        </div>
      </div>

      <div v-if="showSimilarPanel" class="similar-panel">
        <div class="similar-header">
          <h3>相似工单</h3>
          <el-tag type="info" size="small">
            {{ similarTickets.length }} 条结果
          </el-tag>
        </div>

        <el-empty
          v-if="similarTickets.length === 0"
          description="未找到相似工单"
        />
        <div v-else class="similar-list">
          <div
            v-for="item in similarTickets"
            :key="item.ticket.id"
            class="similar-card"
          >
            <div class="similar-card-header">
              <strong>{{ item.ticket.title }}</strong>
              <StatusBadge :status="item.ticket.status" type="ticket" />
            </div>
            <p class="similar-desc">{{ item.ticket.description }}</p>
            <div class="similar-meta">
              <span>相似度：{{ formatSimilarity(item.similarity) }}</span>
              <span>{{ item.ticket.fault_category }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </section>
</template>

<style scoped>
.ticket-detail-panel {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.loading-placeholder {
  min-height: 200px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  padding-bottom: 20px;
  border-bottom: 2px solid;
  border-image: linear-gradient(90deg, var(--color-terracotta-300), var(--color-amber-300), transparent) 1;
}

.detail-title-area {
  display: grid;
  gap: 8px;
}

.detail-eyebrow {
  color: var(--color-terracotta-600);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  font-family: "Inter", sans-serif;
}

.detail-title-area h2 {
  margin: 0;
  font-size: 28px;
  line-height: 1.25;
  color: var(--color-earth-900);
  font-family: "Fraunces", "LXGW WenKai", serif;
  font-weight: 600;
  font-variation-settings: "soft" 70;
}

.detail-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.meta-category {
  color: var(--color-earth-600);
  font-size: 13px;
  padding: 2px 8px;
  border-radius: 8px;
  background: rgba(179, 159, 127, 0.12);
}

.detail-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.detail-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-section h3 {
  margin: 0 0 10px;
  font-size: 16px;
  font-family: "Fraunces", "LXGW WenKai", serif;
  font-weight: 600;
  color: var(--color-earth-900);
}

.description-text {
  margin: 0;
  color: var(--color-earth-800);
  line-height: 1.8;
  font-size: 15px;
  white-space: pre-wrap;
  padding: 16px 18px;
  border-radius: 14px 18px 16px 20px / 16px 20px 18px 14px;
  background: linear-gradient(135deg, rgba(255, 254, 249, 0.95), rgba(249, 246, 240, 0.9));
  border: 1.5px solid var(--color-earth-300);
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.detail-item {
  padding: 14px 16px;
  border-radius: 12px;
  background: rgba(249, 246, 240, 0.6);
  border: 1px solid rgba(201, 184, 154, 0.15);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item span {
  color: var(--color-earth-600);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-family: "Inter", sans-serif;
}

.detail-item strong {
  color: var(--color-earth-900);
  font-size: 14px;
  font-weight: 600;
  font-family: "LXGW WenKai", serif;
}

.similar-panel {
  padding-top: 20px;
  border-top: 2px solid;
  border-image: linear-gradient(90deg, var(--color-moss-300), var(--color-amber-300), transparent) 1;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.similar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.similar-header h3 {
  margin: 0;
  font-size: 16px;
  font-family: "Fraunces", "LXGW WenKai", serif;
  font-weight: 600;
  color: var(--color-earth-900);
}

.similar-list {
  display: grid;
  gap: 12px;
}

.similar-card {
  padding: 16px 18px;
  border-radius: 14px 18px 16px 20px / 16px 20px 18px 14px;
  background: linear-gradient(135deg, rgba(246, 248, 244, 0.95), rgba(233, 240, 227, 0.9));
  border: 1.5px solid var(--color-moss-300);
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: 0 2px 8px rgba(90, 119, 69, 0.08);
  transition: all 0.3s ease;
}

.similar-card:hover {
  border-color: var(--color-moss-400);
  box-shadow: 0 4px 12px rgba(90, 119, 69, 0.12);
  transform: translateY(-1px);
}

.similar-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.similar-card-header strong {
  font-family: "Fraunces", "LXGW WenKai", serif;
  font-weight: 600;
  color: var(--color-earth-900);
  font-size: 15px;
}

.similar-desc {
  margin: 0;
  color: var(--color-earth-700);
  line-height: 1.6;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.similar-meta {
  display: flex;
  gap: 12px;
  color: var(--color-moss-700);
  font-size: 12px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
  }

  .detail-actions {
    width: 100%;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
