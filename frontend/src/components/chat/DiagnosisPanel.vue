<script setup lang="ts">
import { computed, ref } from "vue"

interface DiagnosisStep {
  order: number
  action: string
  expected: string
  next_if_pass: number
  next_if_fail: number
}

interface StepResult {
  order: number
  passed: boolean
}

const props = withDefaults(defineProps<{
  steps?: DiagnosisStep[]
  resolution?: string
}>(), {
  steps: () => [],
  resolution: '',
})

const emit = defineEmits<{
  answer: [stepOrder: number, passed: boolean]
  complete: [results: StepResult[]]
}>()

const currentStepIndex = ref(0)
const stepResults = ref<StepResult[]>([])
const isComplete = ref(false)

const currentStep = computed(() => {
  if (currentStepIndex.value >= props.steps.length) return null
  return props.steps[currentStepIndex.value]
})

const progressPercent = computed(() => {
  if (props.steps.length === 0) return 0
  return Math.round((stepResults.value.length / props.steps.length) * 100)
})

const passedCount = computed(() => stepResults.value.filter((r) => r.passed).length)
const failedCount = computed(() => stepResults.value.filter((r) => !r.passed).length)

function handleAnswer(passed: boolean) {
  if (!currentStep.value) return

  const step = currentStep.value
  stepResults.value.push({ order: step.order, passed })

  emit("answer", step.order, passed)

  const nextIndex = passed ? step.next_if_pass : step.next_if_fail

  if (nextIndex <= 0 || nextIndex > props.steps.length) {
    isComplete.value = true
    emit("complete", stepResults.value)
    return
  }

  currentStepIndex.value = nextIndex - 1

  if (currentStepIndex.value >= props.steps.length) {
    isComplete.value = true
    emit("complete", stepResults.value)
  }
}

function resetDiagnosis() {
  currentStepIndex.value = 0
  stepResults.value = []
  isComplete.value = false
}
</script>

<template>
  <section class="diagnosis-panel">
    <header class="panel-header">
      <div class="panel-title-area">
        <span class="panel-eyebrow">故障诊断</span>
        <h2>诊断流程</h2>
      </div>
      <div class="progress-area">
        <el-progress
          :percentage="progressPercent"
          :stroke-width="8"
          :color="'var(--color-terracotta-500)'"
        />
        <span class="progress-label">{{ stepResults.length }} / {{ steps.length }} 步</span>
      </div>
    </header>

    <div v-if="steps.length === 0" class="empty-state">
      <el-empty description="暂无诊断步骤，请先关联SOP。" />
    </div>

    <template v-else>
      <div v-if="!isComplete && currentStep" class="step-active">
        <div class="step-card">
          <div class="step-indicator">
            <span class="step-number">{{ currentStep.order }}</span>
            <span class="step-total">/ {{ steps.length }}</span>
          </div>
          <div class="step-content">
            <h3>操作</h3>
            <p>{{ currentStep.action }}</p>
            <h3>预期结果</h3>
            <p>{{ currentStep.expected }}</p>
          </div>
        </div>

        <div class="step-actions">
          <el-button
            type="success"
            size="large"
            @click="handleAnswer(true)"
          >
            通过
          </el-button>
          <el-button
            type="danger"
            size="large"
            @click="handleAnswer(false)"
          >
            不通过
          </el-button>
        </div>
      </div>

      <div v-if="isComplete" class="step-complete">
        <div class="complete-card">
          <div class="complete-icon">
            <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
          </div>
          <h3>诊断完成</h3>
          <div class="result-summary">
            <div class="result-item pass">
              <strong>{{ passedCount }}</strong>
              <span>通过</span>
            </div>
            <div class="result-item fail">
              <strong>{{ failedCount }}</strong>
              <span>不通过</span>
            </div>
          </div>
          <div v-if="resolution" class="resolution">
            <h4>解决方案</h4>
            <p>{{ resolution }}</p>
          </div>
        </div>

        <el-button @click="resetDiagnosis">
          重新诊断
        </el-button>
      </div>

      <div v-if="stepResults.length > 0" class="step-history">
        <h4>诊断记录</h4>
        <div class="history-list">
          <div
            v-for="result in stepResults"
            :key="result.order"
            class="history-item"
            :class="{ passed: result.passed, failed: !result.passed }"
          >
            <span class="history-order">步骤 {{ result.order }}</span>
            <span class="history-status">{{ result.passed ? "通过" : "不通过" }}</span>
          </div>
        </div>
      </div>
    </template>
  </section>
</template>

<style scoped>
.diagnosis-panel {
  display: flex;
  flex-direction: column;
  gap: 22px;
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

.progress-area {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-end;
  min-width: 180px;
}

.progress-label {
  font-size: 12px;
  color: var(--color-earth-600);
  font-family: "Inter", sans-serif;
  font-weight: 500;
}

.empty-state {
  padding: 20px 0;
}

.step-card {
  padding: 24px;
  border-radius: 16px 20px 18px 22px / 18px 22px 20px 16px;
  background: linear-gradient(135deg, rgba(255, 254, 249, 0.95), rgba(249, 246, 240, 0.9));
  border: 2px solid var(--color-earth-300);
  box-shadow: 0 4px 16px rgba(90, 70, 50, 0.08);
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 16px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(245, 165, 42, 0.12), rgba(209, 102, 69, 0.08));
  border: 1.5px solid var(--color-terracotta-300);
  flex-shrink: 0;
}

.step-number {
  font-size: 28px;
  font-family: "Fraunces", serif;
  font-weight: 600;
  color: var(--color-terracotta-700);
  line-height: 1;
}

.step-total {
  font-size: 12px;
  color: var(--color-terracotta-600);
  font-family: "Inter", sans-serif;
  font-weight: 500;
}

.step-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.step-content h3 {
  margin: 0;
  font-size: 12px;
  font-weight: 600;
  color: var(--color-earth-600);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-family: "Inter", sans-serif;
}

.step-content p {
  margin: 0;
  color: var(--color-earth-900);
  line-height: 1.7;
  font-size: 15px;
}

.step-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  padding-top: 8px;
}

.step-actions .el-button {
  min-width: 140px;
  font-size: 16px;
  padding: 14px 28px;
  border-radius: 14px 18px 16px 20px / 16px 20px 18px 14px;
}

.complete-card {
  padding: 32px;
  border-radius: 16px 20px 18px 22px / 18px 22px 20px 16px;
  background: linear-gradient(135deg, rgba(246, 248, 244, 0.95), rgba(233, 240, 227, 0.9));
  border: 2px solid var(--color-moss-300);
  box-shadow: 0 4px 16px rgba(90, 119, 69, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  text-align: center;
}

.complete-icon {
  color: var(--color-moss-600);
}

.complete-card h3 {
  margin: 0;
  font-size: 22px;
  font-family: "Fraunces", "LXGW WenKai", serif;
  font-weight: 600;
  color: var(--color-moss-800);
}

.result-summary {
  display: flex;
  gap: 24px;
}

.result-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 20px;
  border-radius: 12px;
}

.result-item.pass {
  background: rgba(116, 149, 91, 0.12);
  border: 1px solid var(--color-moss-300);
}

.result-item.fail {
  background: rgba(209, 102, 69, 0.12);
  border: 1px solid var(--color-terracotta-300);
}

.result-item strong {
  font-size: 24px;
  font-family: "Fraunces", serif;
  font-weight: 600;
}

.result-item.pass strong {
  color: var(--color-moss-700);
}

.result-item.fail strong {
  color: var(--color-terracotta-700);
}

.result-item span {
  font-size: 12px;
  color: var(--color-earth-600);
  font-weight: 500;
}

.resolution {
  width: 100%;
  text-align: left;
  padding-top: 12px;
  border-top: 1px solid var(--color-moss-300);
}

.resolution h4 {
  margin: 0 0 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-moss-700);
}

.resolution p {
  margin: 0;
  color: var(--color-earth-800);
  line-height: 1.7;
  font-size: 14px;
}

.step-history {
  padding-top: 16px;
  border-top: 1px solid rgba(201, 184, 154, 0.2);
}

.step-history h4 {
  margin: 0 0 10px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-earth-700);
  font-family: "Inter", sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.history-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
}

.history-item.passed {
  background: rgba(116, 149, 91, 0.12);
  border: 1px solid var(--color-moss-300);
  color: var(--color-moss-700);
}

.history-item.failed {
  background: rgba(209, 102, 69, 0.12);
  border: 1px solid var(--color-terracotta-300);
  color: var(--color-terracotta-700);
}

.history-order {
  font-weight: 600;
}

.history-status {
  font-weight: 500;
}

@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
  }

  .progress-area {
    align-items: flex-start;
    min-width: auto;
    width: 100%;
  }

  .step-card {
    flex-direction: column;
    gap: 14px;
  }

  .step-actions {
    flex-direction: column;
  }

  .step-actions .el-button {
    width: 100%;
  }
}
</style>
