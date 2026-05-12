<script setup lang="ts">
import { computed } from "vue"

const props = defineProps<{
  status: string
  type: "product" | "ticket" | "manual"
}>()

const colorMap: Record<string, Record<string, { bg: string; text: string; border: string }>> = {
  product: {
    active: { bg: "rgba(116, 149, 91, 0.12)", text: "var(--color-moss-700)", border: "var(--color-moss-300)" },
    deprecated: { bg: "rgba(179, 159, 127, 0.15)", text: "var(--color-earth-600)", border: "var(--color-earth-300)" },
  },
  ticket: {
    open: { bg: "rgba(245, 165, 42, 0.12)", text: "var(--color-amber-700)", border: "var(--color-amber-300)" },
    in_progress: { bg: "rgba(116, 149, 91, 0.12)", text: "var(--color-moss-700)", border: "var(--color-moss-300)" },
    resolved: { bg: "rgba(116, 149, 91, 0.18)", text: "var(--color-moss-800)", border: "var(--color-moss-400)" },
    closed: { bg: "rgba(179, 159, 127, 0.15)", text: "var(--color-earth-600)", border: "var(--color-earth-300)" },
  },
  manual: {
    pending: { bg: "rgba(245, 165, 42, 0.12)", text: "var(--color-amber-700)", border: "var(--color-amber-300)" },
    processing: { bg: "rgba(116, 149, 91, 0.12)", text: "var(--color-moss-700)", border: "var(--color-moss-300)" },
    completed: { bg: "rgba(116, 149, 91, 0.18)", text: "var(--color-moss-800)", border: "var(--color-moss-400)" },
    failed: { bg: "rgba(209, 102, 69, 0.12)", text: "var(--color-terracotta-700)", border: "var(--color-terracotta-300)" },
  },
}

const labelMap: Record<string, Record<string, string>> = {
  product: { active: "活跃", deprecated: "已弃用" },
  ticket: { open: "待处理", in_progress: "处理中", resolved: "已解决", closed: "已关闭" },
  manual: { pending: "待处理", processing: "处理中", completed: "已完成", failed: "失败" },
}

const colors = computed(() => {
  const typeMap = colorMap[props.type]
  return typeMap?.[props.status] ?? { bg: "rgba(179, 159, 127, 0.1)", text: "var(--color-earth-600)", border: "var(--color-earth-300)" }
})

const label = computed(() => {
  const typeMap = labelMap[props.type]
  return typeMap?.[props.status] ?? props.status
})
</script>

<template>
  <span
    class="status-badge"
    :style="{
      backgroundColor: colors.bg,
      color: colors.text,
      borderColor: colors.border,
    }"
  >
    {{ label }}
  </span>
</template>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 8px 10px 9px 11px / 9px 11px 10px 8px;
  border: 1px solid;
  font-size: 12px;
  font-weight: 600;
  font-family: "Inter", sans-serif;
  line-height: 1.4;
  white-space: nowrap;
  transition: all 0.2s ease;
}
</style>
