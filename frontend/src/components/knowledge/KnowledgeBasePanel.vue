<script setup lang="ts">
import { computed, onMounted, ref } from "vue"

import { useKnowledgeStore } from "@/stores/knowledge"
import { useProductStore } from "@/stores/products"
import type { CreateSOPPayload } from "@/services/knowledge"
import StatusBadge from "@/components/common/StatusBadge.vue"

const knowledgeStore = useKnowledgeStore()
const productStore = useProductStore()

const activeTab = ref("manuals")
const selectedProductId = ref("")

const showUploadDialog = ref(false)
const showImportDialog = ref(false)
const showSopDialog = ref(false)

const uploadForm = ref({ title: "" })
const uploadFile = ref<File | null>(null)
const importForm = ref({ source: "" })

const sopForm = ref<CreateSOPPayload>({
  product_id: "",
  fault_type: "",
  fault_category: "",
  symptoms: [{ keyword: "", weight: 1 }],
  steps: [{ order: 1, action: "", expected: "", next_if_pass: 0, next_if_fail: 0 }],
  resolution: "",
})

const products = computed(() => productStore.items)

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  uploadFile.value = input.files?.[0] ?? null
}

async function handleUpload() {
  if (!uploadFile.value || !selectedProductId.value || !uploadForm.value.title) return
  await knowledgeStore.uploadManual(uploadFile.value, {
    product_id: selectedProductId.value,
    title: uploadForm.value.title,
  })
  showUploadDialog.value = false
  uploadForm.value = { title: "" }
  uploadFile.value = null
}

async function handleImport() {
  if (!selectedProductId.value || !importForm.value.source) return
  await knowledgeStore.importSpecs({
    product_id: selectedProductId.value,
    source: importForm.value.source,
  })
  showImportDialog.value = false
  importForm.value = { source: "" }
}

function addSymptom() {
  sopForm.value.symptoms.push({ keyword: "", weight: 1 })
}

function removeSymptom(index: number) {
  sopForm.value.symptoms.splice(index, 1)
}

function addStep() {
  const nextOrder = sopForm.value.steps.length + 1
  sopForm.value.steps.push({ order: nextOrder, action: "", expected: "", next_if_pass: 0, next_if_fail: 0 })
}

function removeStep(index: number) {
  sopForm.value.steps.splice(index, 1)
  sopForm.value.steps.forEach((step, i) => {
    step.order = i + 1
  })
}

async function handleCreateSop() {
  if (!selectedProductId.value || !sopForm.value.fault_type || !sopForm.value.fault_category) return
  await knowledgeStore.createSOP({
    ...sopForm.value,
    product_id: selectedProductId.value,
  })
  showSopDialog.value = false
  sopForm.value = {
    product_id: "",
    fault_type: "",
    fault_category: "",
    symptoms: [{ keyword: "", weight: 1 }],
    steps: [{ order: 1, action: "", expected: "", next_if_pass: 0, next_if_fail: 0 }],
    resolution: "",
  }
}

async function onProductChange() {
  if (!selectedProductId.value) return
  if (activeTab.value === "manuals") {
    await knowledgeStore.fetchManuals(selectedProductId.value)
  } else if (activeTab.value === "specs") {
    await knowledgeStore.fetchSpecs(selectedProductId.value)
  } else {
    await knowledgeStore.fetchSOPs(selectedProductId.value)
  }
}

async function onTabChange(tab: string | number) {
  if (!selectedProductId.value) return
  const tabName = String(tab)
  if (tabName === "manuals") {
    await knowledgeStore.fetchManuals(selectedProductId.value)
  } else if (tabName === "specs") {
    await knowledgeStore.fetchSpecs(selectedProductId.value)
  } else {
    await knowledgeStore.fetchSOPs(selectedProductId.value)
  }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("zh-CN")
}

onMounted(() => {
  void productStore.fetchProducts()
})
</script>

<template>
  <section class="knowledge-panel">
    <header class="panel-header">
      <div class="panel-title-area">
        <span class="panel-eyebrow">知识库管理</span>
        <h2>知识库</h2>
        <p>管理产品手册、技术参数和故障诊断SOP。</p>
      </div>
    </header>

    <el-alert
      v-if="knowledgeStore.error"
      :closable="false"
      type="error"
      show-icon
      title="操作失败"
      :description="knowledgeStore.error"
    />

    <div class="product-selector">
      <el-select
        v-model="selectedProductId"
        placeholder="选择产品"
        clearable
        class="product-select"
        @change="onProductChange"
      >
        <el-option
          v-for="product in products"
          :key="product.id"
          :label="product.name"
          :value="product.id"
        />
      </el-select>
    </div>

    <el-tabs v-model="activeTab" class="knowledge-tabs" @tab-change="onTabChange">
      <el-tab-pane label="手册管理" name="manuals">
        <div class="tab-actions">
          <el-button
            type="primary"
            size="small"
            :disabled="!selectedProductId"
            @click="showUploadDialog = true"
          >
            上传手册
          </el-button>
        </div>

        <el-empty v-if="!selectedProductId" description="请先选择产品" />
        <el-empty
          v-else-if="knowledgeStore.manuals.length === 0"
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
        <div class="tab-actions">
          <el-button
            type="primary"
            size="small"
            :disabled="!selectedProductId"
            @click="showImportDialog = true"
          >
            导入参数
          </el-button>
        </div>

        <el-empty v-if="!selectedProductId" description="请先选择产品" />
        <el-empty
          v-else-if="knowledgeStore.specs.length === 0"
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
        <div class="tab-actions">
          <el-button
            type="primary"
            size="small"
            :disabled="!selectedProductId"
            @click="showSopDialog = true"
          >
            创建SOP
          </el-button>
        </div>

        <el-empty v-if="!selectedProductId" description="请先选择产品" />
        <el-empty
          v-else-if="knowledgeStore.sops.length === 0"
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
              <span class="symptoms-label">症状：</span>
              <el-tag
                v-for="(symptom, idx) in sop.symptoms"
                :key="idx"
                size="small"
                effect="light"
                class="symptom-tag"
              >
                {{ symptom.keyword }}
              </el-tag>
            </div>
            <div class="sop-steps-count">
              诊断步骤：{{ sop.steps.length }} 步
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog
      v-model="showUploadDialog"
      title="上传手册"
      width="480px"
      :close-on-click-modal="false"
    >
      <el-form label-position="top">
        <el-form-item label="手册标题" required>
          <el-input v-model="uploadForm.title" placeholder="请输入手册标题" />
        </el-form-item>
        <el-form-item label="选择文件" required>
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            class="file-input"
            @change="handleFileChange"
          >
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="!uploadForm.title || !uploadFile"
          @click="handleUpload"
        >
          上传
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showImportDialog"
      title="导入参数"
      width="480px"
      :close-on-click-modal="false"
    >
      <el-form label-position="top">
        <el-form-item label="数据来源" required>
          <el-input v-model="importForm.source" placeholder="请输入参数数据来源" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="!importForm.source"
          @click="handleImport"
        >
          导入
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showSopDialog"
      title="创建SOP"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form label-position="top">
        <el-form-item label="故障类型" required>
          <el-input v-model="sopForm.fault_type" placeholder="请输入故障类型" />
        </el-form-item>
        <el-form-item label="故障分类" required>
          <el-input v-model="sopForm.fault_category" placeholder="请输入故障分类" />
        </el-form-item>
        <el-form-item label="症状关键词">
          <div class="dynamic-list">
            <div
              v-for="(symptom, idx) in sopForm.symptoms"
              :key="idx"
              class="dynamic-item"
            >
              <el-input v-model="symptom.keyword" placeholder="关键词" class="symptom-input" />
              <el-input-number v-model="symptom.weight" :min="0" :max="10" :step="0.1" size="small" />
              <el-button
                v-if="sopForm.symptoms.length > 1"
                type="danger"
                plain
                size="small"
                @click="removeSymptom(idx)"
              >
                移除
              </el-button>
            </div>
          </div>
          <el-button size="small" @click="addSymptom">添加症状</el-button>
        </el-form-item>
        <el-form-item label="诊断步骤">
          <div class="dynamic-list">
            <div
              v-for="(step, idx) in sopForm.steps"
              :key="idx"
              class="dynamic-item step-item"
            >
              <span class="step-order">{{ step.order }}.</span>
              <el-input v-model="step.action" placeholder="操作" class="step-input" />
              <el-input v-model="step.expected" placeholder="预期结果" class="step-input" />
              <el-button
                v-if="sopForm.steps.length > 1"
                type="danger"
                plain
                size="small"
                @click="removeStep(idx)"
              >
                移除
              </el-button>
            </div>
          </div>
          <el-button size="small" @click="addStep">添加步骤</el-button>
        </el-form-item>
        <el-form-item label="解决方案">
          <el-input
            v-model="sopForm.resolution"
            type="textarea"
            :rows="3"
            placeholder="请输入解决方案"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSopDialog = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="!sopForm.fault_type || !sopForm.fault_category"
          @click="handleCreateSop"
        >
          创建
        </el-button>
      </template>
    </el-dialog>
  </section>
</template>

<style scoped>
.knowledge-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel-header {
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

.product-selector {
  display: flex;
  gap: 12px;
  align-items: center;
}

.product-select {
  max-width: 280px;
}

.tab-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 14px;
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

.sop-steps-count {
  font-size: 12px;
  color: var(--color-earth-600);
}

.file-input {
  width: 100%;
  padding: 8px;
  border: 1.5px dashed var(--color-earth-300);
  border-radius: 10px;
  background: rgba(249, 246, 240, 0.6);
  color: var(--color-earth-700);
  font-family: "LXGW WenKai", serif;
  cursor: pointer;
  transition: all 0.2s ease;
}

.file-input:hover {
  border-color: var(--color-terracotta-400);
  background: rgba(249, 246, 240, 0.9);
}

.dynamic-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.dynamic-item {
  display: flex;
  gap: 8px;
  align-items: center;
}

.symptom-input {
  flex: 1;
}

.step-item {
  gap: 6px;
}

.step-order {
  font-weight: 600;
  color: var(--color-earth-700);
  font-size: 13px;
  min-width: 20px;
}

.step-input {
  flex: 1;
}

:deep(.knowledge-tabs .el-tabs__item) {
  font-family: "LXGW WenKai", serif;
  font-weight: 600;
  font-size: 14px;
}

:deep(.knowledge-tabs .el-tabs__active-bar) {
  background: linear-gradient(90deg, var(--color-terracotta-500), var(--color-amber-400));
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
}

:deep(.el-table td.el-table__cell) {
  font-family: "LXGW WenKai", serif;
  font-size: 14px;
  color: var(--color-earth-800);
}

@media (max-width: 768px) {
  .product-select {
    max-width: 100%;
  }

  .dynamic-item {
    flex-wrap: wrap;
  }
}
</style>
