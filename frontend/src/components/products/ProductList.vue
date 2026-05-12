<script setup lang="ts">
import { computed, onMounted, ref } from "vue"

import { useProductStore } from "@/stores/products"
import type { ProductForm } from "@/types/product"
import StatusBadge from "@/components/common/StatusBadge.vue"

const productStore = useProductStore()

const searchQuery = ref("")
const categoryFilter = ref("")
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const editingProductId = ref<string | null>(null)

const formDefaults: ProductForm = { name: "", category: "", version: "" }
const createForm = ref<ProductForm>({ ...formDefaults })
const editForm = ref<ProductForm>({ ...formDefaults })

const categories = computed(() => {
  const set = new Set(productStore.items.map((p) => p.category))
  return Array.from(set).sort()
})

const filteredProducts = computed(() => {
  let items = productStore.items

  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    items = items.filter(
      (p) =>
        p.name.toLowerCase().includes(query) ||
        p.category.toLowerCase().includes(query),
    )
  }

  if (categoryFilter.value) {
    items = items.filter((p) => p.category === categoryFilter.value)
  }

  return items
})

function openCreate() {
  createForm.value = { ...formDefaults }
  showCreateDialog.value = true
}

async function handleCreate() {
  await productStore.createProduct(createForm.value)
  showCreateDialog.value = false
}

function openEdit(productId: string) {
  const product = productStore.items.find((p) => p.id === productId)
  if (!product) return
  editingProductId.value = productId
  editForm.value = { name: product.name, category: product.category, version: product.version }
  showEditDialog.value = true
}

async function handleEdit() {
  if (!editingProductId.value) return
  await productStore.updateProduct(editingProductId.value, editForm.value)
  showEditDialog.value = false
  editingProductId.value = null
}

async function handleDelete(productId: string) {
  await productStore.deleteProduct(productId)
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("zh-CN")
}

onMounted(() => {
  void productStore.fetchProducts()
})
</script>

<template>
  <section class="product-list-panel">
    <header class="panel-header">
      <div class="panel-title-area">
        <span class="panel-eyebrow">产品管理</span>
        <h2>产品列表</h2>
        <p>管理所有产品信息，包括创建、编辑和删除操作。</p>
      </div>
      <el-button type="primary" @click="openCreate">
        新建产品
      </el-button>
    </header>

    <el-alert
      v-if="productStore.error"
      :closable="false"
      type="error"
      show-icon
      title="操作失败"
      :description="productStore.error"
    />

    <div class="filter-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索产品名称或类别..."
        clearable
        class="filter-input"
      >
        <template #prefix>
          <el-icon><svg viewBox="0 0 1024 1024" width="14" height="14"><path fill="currentColor" d="M909.6 854.5L649.9 594.8C690.2 542.7 714 478.4 714 408c0-167.6-136.4-304-304-304S106 240.4 106 408s136.4 304 304 304c70.4 0 134.7-23.8 186.8-64.2l259.7 259.6a8.2 8.2 0 0011.6 0l41.5-41.5a8.2 8.2 0 000-11.6zM410 676c-147.1 0-266-118.9-266-266s118.9-266 266-266 266 118.9 266 266-118.9 266-266 266z"/></svg></el-icon>
        </template>
      </el-input>
      <el-select
        v-model="categoryFilter"
        placeholder="按类别筛选"
        clearable
        class="filter-select"
      >
        <el-option
          v-for="cat in categories"
          :key="cat"
          :label="cat"
          :value="cat"
        />
      </el-select>
      <div class="filter-summary">
        <el-tag type="info" size="small">
          共 {{ filteredProducts.length }} 项
        </el-tag>
      </div>
    </div>

    <el-empty
      v-if="!productStore.isLoading && filteredProducts.length === 0"
      description="暂无产品数据"
    />

    <el-table
      v-else
      v-loading="productStore.isLoading"
      :data="filteredProducts"
      stripe
      class="product-table"
    >
      <el-table-column prop="name" label="产品名称" min-width="160">
        <template #default="{ row }">
          <strong class="product-name">{{ row.name }}</strong>
        </template>
      </el-table-column>
      <el-table-column prop="category" label="类别" width="140" />
      <el-table-column prop="version" label="版本" width="100" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <StatusBadge :status="row.status" type="product" />
        </template>
      </el-table-column>
      <el-table-column prop="updated_at" label="更新时间" width="130">
        <template #default="{ row }">
          {{ formatDate(row.updated_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row.id)">
            编辑
          </el-button>
          <el-popconfirm
            title="确认删除该产品？"
            confirm-button-text="删除"
            cancel-button-text="取消"
            @confirm="handleDelete(row.id)"
          >
            <template #reference>
              <el-button type="danger" plain size="small">
                删除
              </el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="showCreateDialog"
      title="新建产品"
      width="480px"
      :close-on-click-modal="false"
    >
      <el-form :model="createForm" label-width="80px" label-position="top">
        <el-form-item label="产品名称" required>
          <el-input v-model="createForm.name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="类别" required>
          <el-input v-model="createForm.category" placeholder="请输入产品类别" />
        </el-form-item>
        <el-form-item label="版本" required>
          <el-input v-model="createForm.version" placeholder="请输入产品版本" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="!createForm.name || !createForm.category || !createForm.version"
          @click="handleCreate"
        >
          创建
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showEditDialog"
      title="编辑产品"
      width="480px"
      :close-on-click-modal="false"
    >
      <el-form :model="editForm" label-width="80px" label-position="top">
        <el-form-item label="产品名称" required>
          <el-input v-model="editForm.name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="类别" required>
          <el-input v-model="editForm.category" placeholder="请输入产品类别" />
        </el-form-item>
        <el-form-item label="版本" required>
          <el-input v-model="editForm.version" placeholder="请输入产品版本" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="!editForm.name || !editForm.category || !editForm.version"
          @click="handleEdit"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
  </section>
</template>

<style scoped>
.product-list-panel {
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

.filter-input {
  max-width: 280px;
}

.filter-select {
  max-width: 180px;
}

.filter-summary {
  margin-left: auto;
}

.product-name {
  font-family: "Fraunces", "LXGW WenKai", serif;
  font-weight: 600;
  color: var(--color-earth-900);
}

.product-table {
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

  .filter-input,
  .filter-select {
    max-width: 100%;
  }
}
</style>
