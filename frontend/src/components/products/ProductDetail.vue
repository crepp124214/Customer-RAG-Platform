<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue"

import { useProductStore } from "@/stores/products"
import { useKnowledgeStore } from "@/stores/knowledge"
import StatusBadge from "@/components/common/StatusBadge.vue"

const props = defineProps<{
  productId: string
}>()

const productStore = useProductStore()
const knowledgeStore = useKnowledgeStore()

const activeTab = ref("manuals")

const product = computed(() => productStore.currentProduct)

const manualCount = computed(() => knowledgeStore.manuals.length)
const specCount = computed(() => knowledgeStore.specs.length)
const sopCount = computed(() => knowledgeStore.sops.length)

async function loadProductData() {
  await productStore.fetchProduct(props.productId)
  await knowledgeStore.fetchManuals(props.productId)
  await knowledgeStore.fetchSpecs(props.productId)
  await knowledgeStore.fetchSOPs(props.productId)
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("zh-CN")
}

watch(() => props.productId, () => {
  void loadProductData()
})

onMounted(() => {
  void loadProductData()
})
</script>

<template>
  <section class="product-detail-panel">
    <el-alert
      v-if="productStore.error"
      :closable="false"
      type="error"
      show-icon
      title="加载失败"
      :description="productStore.error"
    />

    <div v-if="productStore.isLoading" v-loading="true" class="loading-placeholder" />

    <template v-if="product">
      <header class="detail-header">
        <div class="detail-title-area">
          <span class="detail-eyebrow">产品详情</span>
          <h2>{{ product.name }}</h2>
          <div class="detail-meta">
            <StatusBadge :status="product.status" type="product" />
            <span class="meta-divider">|</span>
            <span>{{ product.category }}</span>
            <span class="meta-divider">|</span>
            <span>版本 {{ product.version }}</span>
          </div>
        </div>
        <div class="detail-timestamps">
          <span>创建于 {{ formatDate(product.created_at) }}</span>
          <span>更新于 {{ formatDate(product.updated_at) }}</span>
        </div>
      </header>

      <div class="knowledge-summary">
        <div class="summary-card">
          <strong>{{ manualCount }}</strong>
          <span>手册</span>
        </div>
        <div class="summary-card">
          <strong>{{ specCount }}</strong>
          <span>参数</span>
        </div>
        <div class="summary-card">
          <strong>{{ sopCount }}</strong>
          <span>SOP</span>
        </div>
      </div>

      <el-tabs v-model="activeTab" class="detail-tabs">
        <el-tab-pane label="手册管理" name="manuals">
          <el-empty
            v-if="knowledgeStore.manuals.length === 0"
            description="该产品暂无手册"
          />
          <div v-else class="knowledge-list">
            <div
              v-for="manual in knowledgeStore.manuals"
              :key="manual.id"
              class="knowledge-card"
            >
              <div class="card-header">
                <strong>{{ manual.title }}</strong>
                <StatusBadge :status="manual.status" type="manual" />
              </div>
              <div class="card-meta">
                <span>{{ manual.file_type }}</span>
                <span>{{ formatDate(manual.updated_at) }}</span>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="参数管理" name="specs">
          <el-empty
            v-if="knowledgeStore.specs.length === 0"
            description="该产品暂无参数"
          />
          <el-table
            v-else
            :data="knowledgeStore.specs"
            stripe
            size="small"
          >
            <el-table-column prop="spec_name" label="参数名" min-width="140" />
            <el-table-column prop="spec_value" label="参数值" min-width="140" />
            <el-table-column prop="spec_category" label="分类" width="120" />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="SOP管理" name="sops">
          <el-empty
            v-if="knowledgeStore.sops.length === 0"
            description="该产品暂无SOP"
          />
          <div v-else class="knowledge-list">
            <div
              v-for="sop in knowledgeStore.sops"
              :key="sop.id"
              class="knowledge-card sop-card"
            >
              <div class="card-header">
                <strong>{{ sop.fault_type }}</strong>
                <el-tag size="small" effect="plain">{{ sop.fault_category }}</el-tag>
              </div>
              <div class="sop-symptoms">
                <span class="symptoms-label">症状关键词：</span>
                <el-tag
                  v-for="(symptom, idx) in sop.symptoms"
                  :key="idx"
                  size="small"
                  effect="light"
                  class="symptom-tag"
                >
                  {{ symptom.keyword }} ({{ symptom.weight }})
                </el-tag>
              </div>
              <div class="sop-steps">
                <span class="steps-label">诊断步骤：{{ sop.steps.length }} 步</span>
              </div>
              <div class="sop-resolution">
                <span>解决方案：{{ sop.resolution }}</span>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </template>
  </section>
</template>

<style scoped>
.product-detail-panel {
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
  color: var(--color-earth-700);
  font-size: 14px;
}

.meta-divider {
  color: var(--color-earth-300);
}

.detail-timestamps {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-end;
  color: var(--color-earth-600);
  font-size: 12px;
  font-family: "Inter", sans-serif;
}

.knowledge-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.summary-card {
  padding: 18px 20px;
  border-radius: 16px 20px 18px 22px / 18px 22px 20px 16px;
  background: linear-gradient(135deg, rgba(246, 248, 244, 0.95), rgba(233, 240, 227, 0.9));
  border: 1.5px solid var(--color-moss-300);
  display: flex;
  flex-direction: column;
  gap: 4px;
  box-shadow: 0 2px 8px rgba(90, 119, 69, 0.08);
  transition: all 0.3s ease;
}

.summary-card:hover {
  border-color: var(--color-moss-400);
  box-shadow: 0 4px 12px rgba(90, 119, 69, 0.12);
  transform: translateY(-1px);
}

.summary-card strong {
  font-size: 28px;
  font-family: "Fraunces", serif;
  font-weight: 600;
  color: var(--color-moss-800);
}

.summary-card span {
  font-size: 13px;
  color: var(--color-moss-700);
}

.knowledge-list {
  display: grid;
  gap: 12px;
}

.knowledge-card {
  padding: 16px 18px;
  border-radius: 14px 18px 16px 20px / 16px 20px 18px 14px;
  background: linear-gradient(135deg, rgba(255, 254, 249, 0.95), rgba(249, 246, 240, 0.9));
  border: 1.5px solid var(--color-earth-300);
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: 0 2px 8px rgba(90, 70, 50, 0.06);
  transition: all 0.3s ease;
}

.knowledge-card:hover {
  border-color: var(--color-earth-400);
  box-shadow: 0 4px 16px rgba(90, 70, 50, 0.1);
  transform: translateY(-1px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.card-header strong {
  font-family: "Fraunces", "LXGW WenKai", serif;
  font-weight: 600;
  color: var(--color-earth-900);
  font-size: 15px;
}

.card-meta {
  display: flex;
  gap: 12px;
  color: var(--color-earth-600);
  font-size: 12px;
}

.sop-card {
  border-color: var(--color-moss-300);
  background: linear-gradient(135deg, rgba(246, 248, 244, 0.95), rgba(233, 240, 227, 0.9));
}

.sop-symptoms {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.symptoms-label {
  font-size: 12px;
  color: var(--color-earth-600);
  font-weight: 600;
}

.symptom-tag {
  font-size: 11px;
}

.sop-steps {
  font-size: 12px;
  color: var(--color-earth-600);
}

.steps-label {
  font-weight: 600;
}

.sop-resolution {
  font-size: 13px;
  color: var(--color-moss-800);
  line-height: 1.6;
}

:deep(.detail-tabs .el-tabs__item) {
  font-family: "LXGW WenKai", serif;
  font-weight: 600;
  font-size: 14px;
}

:deep(.detail-tabs .el-tabs__active-bar) {
  background: linear-gradient(90deg, var(--color-terracotta-500), var(--color-amber-400));
}

@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
  }

  .detail-timestamps {
    align-items: flex-start;
  }

  .knowledge-summary {
    grid-template-columns: 1fr;
  }
}
</style>
