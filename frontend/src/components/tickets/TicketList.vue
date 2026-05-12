<script setup lang="ts">
import { computed, onMounted, ref } from "vue"

import { useTicketStore } from "@/stores/tickets"
import { useProductStore } from "@/stores/products"
import type { CreateTicketPayload } from "@/services/tickets"
import type { Ticket } from "@/types/ticket"
import StatusBadge from "@/components/common/StatusBadge.vue"

const emit = defineEmits<{
  view: [ticketId: string]
}>()

const ticketStore = useTicketStore()
const productStore = useProductStore()

const statusFilter = ref<Ticket["status"] | "">("")
const priorityFilter = ref<Ticket["priority"] | "">("")
const showCreateDialog = ref(false)

const createForm = ref<CreateTicketPayload>({
  product_id: null,
  title: "",
  description: "",
  fault_category: "",
  priority: "medium",
})

const filteredTickets = computed(() => {
  let items = ticketStore.items

  if (statusFilter.value) {
    items = items.filter((t) => t.status === statusFilter.value)
  }

  if (priorityFilter.value) {
    items = items.filter((t) => t.priority === priorityFilter.value)
  }

  return items
})

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

async function handleCreate() {
  if (!createForm.value.title || !createForm.value.description) return
  await ticketStore.createTicket(createForm.value)
  showCreateDialog.value = false
  createForm.value = {
    product_id: null,
    title: "",
    description: "",
    fault_category: "",
    priority: "medium",
  }
}

function openDetail(ticketId: string) {
  emit("view", ticketId)
}

async function handleStatusUpdate(ticketId: string, newStatus: Ticket["status"]) {
  await ticketStore.updateTicketStatus(ticketId, { status: newStatus })
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("zh-CN")
}

onMounted(() => {
  void ticketStore.fetchTickets()
  void productStore.fetchProducts()
})
</script>

<template>
  <section class="ticket-list-panel">
    <header class="panel-header">
      <div class="panel-title-area">
        <span class="panel-eyebrow">工单管理</span>
        <h2>工单列表</h2>
        <p>查看和处理所有客服工单，支持按状态和优先级筛选。</p>
      </div>
      <el-button type="primary" @click="showCreateDialog = true">
        新建工单
      </el-button>
    </header>

    <el-alert
      v-if="ticketStore.error"
      :closable="false"
      type="error"
      show-icon
      title="操作失败"
      :description="ticketStore.error"
    />

    <div class="filter-bar">
      <el-select
        v-model="statusFilter"
        placeholder="按状态筛选"
        clearable
        class="filter-select"
      >
        <el-option label="待处理" value="open" />
        <el-option label="处理中" value="in_progress" />
        <el-option label="已解决" value="resolved" />
        <el-option label="已关闭" value="closed" />
      </el-select>
      <el-select
        v-model="priorityFilter"
        placeholder="按优先级筛选"
        clearable
        class="filter-select"
      >
        <el-option label="低" value="low" />
        <el-option label="中" value="medium" />
        <el-option label="高" value="high" />
        <el-option label="紧急" value="urgent" />
      </el-select>
      <div class="filter-summary">
        <el-tag type="info" size="small">
          共 {{ filteredTickets.length }} 项
        </el-tag>
        <el-tag v-if="ticketStore.openTickets.length > 0" type="warning" size="small">
          待处理 {{ ticketStore.openTickets.length }}
        </el-tag>
      </div>
    </div>

    <el-empty
      v-if="!ticketStore.isLoading && filteredTickets.length === 0"
      description="暂无工单数据"
    />

    <el-table
      v-else
      v-loading="ticketStore.isLoading"
      :data="filteredTickets"
      stripe
      class="ticket-table"
    >
      <el-table-column prop="title" label="标题" min-width="180">
        <template #default="{ row }">
          <el-button link type="primary" class="ticket-title-link" @click="openDetail(row.id)">
            {{ row.title }}
          </el-button>
        </template>
      </el-table-column>
      <el-table-column prop="fault_category" label="故障分类" width="120" />
      <el-table-column prop="priority" label="优先级" width="90">
        <template #default="{ row }">
          <el-tag :type="priorityType[row.priority]" size="small" effect="plain">
            {{ priorityLabel[row.priority] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <StatusBadge :status="row.status" type="ticket" />
        </template>
      </el-table-column>
      <el-table-column prop="updated_at" label="更新时间" width="130">
        <template #default="{ row }">
          {{ formatDate(row.updated_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openDetail(row.id)">
            详情
          </el-button>
          <el-dropdown
            v-if="row.status !== 'closed'"
            trigger="click"
            @command="(cmd: string) => handleStatusUpdate(row.id, cmd as Ticket['status'])"
          >
            <el-button size="small">
              更新状态
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-if="row.status === 'open'" command="in_progress">
                  标记处理中
                </el-dropdown-item>
                <el-dropdown-item v-if="row.status === 'in_progress'" command="resolved">
                  标记已解决
                </el-dropdown-item>
                <el-dropdown-item v-if="row.status === 'resolved'" command="closed">
                  标记已关闭
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="showCreateDialog"
      title="新建工单"
      width="560px"
      :close-on-click-modal="false"
    >
      <el-form :model="createForm" label-position="top">
        <el-form-item label="标题" required>
          <el-input v-model="createForm.title" placeholder="请输入工单标题" />
        </el-form-item>
        <el-form-item label="描述" required>
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="4"
            placeholder="请描述问题详情"
          />
        </el-form-item>
        <el-form-item label="关联产品">
          <el-select
            v-model="createForm.product_id"
            placeholder="选择关联产品（可选）"
            clearable
          >
            <el-option
              v-for="product in productStore.items"
              :key="product.id"
              :label="product.name"
              :value="product.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="故障分类">
          <el-input v-model="createForm.fault_category" placeholder="请输入故障分类" />
        </el-form-item>
        <el-form-item label="优先级" required>
          <el-radio-group v-model="createForm.priority">
            <el-radio value="low">低</el-radio>
            <el-radio value="medium">中</el-radio>
            <el-radio value="high">高</el-radio>
            <el-radio value="urgent">紧急</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="!createForm.title || !createForm.description"
          @click="handleCreate"
        >
          创建
        </el-button>
      </template>
    </el-dialog>
  </section>
</template>

<style scoped>
.ticket-list-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  padding-bottom: 20px;
  border-bottom: 2px solid;
  border-image: linear-gradient(90deg, var(--color-terracotta-300), var(--color-amber-300), transparent) 1;
}

.panel-title-area {
  display: grid;
  gap: 8px;
}

.panel-eyebrow {
  color: var(--color-terracotta-600);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  font-family: "Inter", sans-serif;
}

.panel-title-area h2 {
  margin: 0;
  font-size: 28px;
  line-height: 1.25;
  color: var(--color-earth-900);
  font-family: "Fraunces", "LXGW WenKai", serif;
  font-weight: 600;
  font-variation-settings: "soft" 70;
}

.panel-title-area p {
  margin: 0;
  max-width: 560px;
  color: var(--color-earth-700);
  line-height: 1.7;
  font-size: 14px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-select {
  max-width: 180px;
}

.filter-summary {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.ticket-title-link {
  font-family: "Fraunces", "LXGW WenKai", serif;
  font-weight: 600;
  font-size: 14px;
}

.ticket-table {
  border-radius: var(--radius-organic-md, 14px);
  overflow: hidden;
}

:deep(.el-table) {
  --el-table-border-color: rgba(201, 184, 154, 0.2);
  --el-table-header-bg-color: rgba(249, 246, 240, 0.8);
  --el-table-row-hover-bg-color: rgba(245, 165, 42, 0.06);
}

:deep(.el-table th.el-table__cell) {
  font-family: "Inter", sans-serif;
  font-weight: 600;
  font-size: 12px;
  color: var(--color-earth-700);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

:deep(.el-table td.el-table__cell) {
  font-family: "LXGW WenKai", serif;
  font-size: 14px;
  color: var(--color-earth-800);
}

@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
    gap: 12px;
  }

  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-select {
    max-width: 100%;
  }
}
</style>
