# CLAUDE.md

## 1. 项目定位

本仓库是一个面向客服/售后支持场景的智能知识平台，基于 RAG 架构实现产品手册检索、故障诊断引导、工单知识复用和智能话术推荐。

核心解决四大痛点：
1. 知识检索效率低 — 客服人员无法快速找到产品手册中的答案
2. 故障排查无标准流程 — 缺乏结构化的故障诊断引导
3. 工单知识未复用 — 历史工单的解决方案散落各处
4. 新人上手慢 — 缺乏智能辅助和话术推荐

---

## 2. 核心原则

1. 先做系统设计，再做编码实现。
2. 先明确目标、场景、边界、依赖和风险，再进入细化开发。
3. 优先选择简单、稳定、易维护、易演进的方案。
4. 当前阶段不为未来的复杂场景过度设计。
5. 所有新增能力都要满足模块边界清晰、可扩展、可测试、可维护。
6. 复杂问题必须先拆小，再逐步实现。
7. 必须保留失败路径、边界条件和验证策略，不能只关注成功路径。
8. 本仓库按产品工程标准推进，不再按纯 Demo 思路继续堆功能。

---

## 3. 技术栈

### 前端
- Vue 3 + Vite + Element Plus + Pinia + Axios + SSE

### 后端
- FastAPI + Pydantic + Uvicorn + SQLAlchemy + Alembic

### 异步任务
- RQ + Redis

### 数据层
- PostgreSQL + pgvector

### 模型层
- DashScope / 通义千问（Qwen）
- DashScope Embedding
- BGE Reranker

### 文档解析
- PyMuPDF + pdfplumber

### 部署
- Docker Compose

---

## 4. 阶段边界与禁止事项

### 当前阶段目标

将通用 RAG 系统重构为客服/售后支持智能知识平台：
- 产品知识库管理
- 工单知识库与相似匹配
- 故障诊断引擎
- 智能话术推荐
- 客服专用 Tool Calling
- SSE 流式输出

### 当前阶段禁止引入

- Neo4j / GraphRAG
- 多模态主链路
- 用户认证与权限系统
- 多租户隔离
- 外部系统对接（CRM、工单系统 API）
- 实时语音客服
- 移动端适配
- WebSocket
- Celery

---

## 5. 目标架构与目录规范

### 主目录

```text
frontend/
backend/
worker/
docs/
scripts/
tests/
```

### 后端结构

```text
backend/
  api/
    routes/        — products, knowledge, tickets, chat, diagnosis, system
    schemas/       — products, knowledge, tickets, chat, diagnosis, response
    deps/          — database
  app/
    models/        — product, product_manual, product_spec, fault_sop, ticket, chunk, session, message, task
    services/      — product, knowledge_base, ticket, diagnosis, customer_service_qa, script_recommend, chat, retrieval, chunking, parser, document, system
    repositories/  — product, ticket, spec, fault_sop, chunk, document, session, message, task
    orchestrators/ — knowledge_ingestion
    tasks/         — knowledge_tasks, system_tasks
    tools/         — product_spec_lookup, ticket_search, fault_diagnosis, sop_lookup, base, registry, orchestrator, gating
    settings/      — config
  infrastructure/
    database/      — PostgreSQL + pgvector + Alembic migrations
    vector/        — pgvector 向量检索
    llm/           — DashScope/Qwen 客户端
    queue/         — RQ + Redis
    storage/       — 文件存储
    observability/ — 日志与监控
  tests/
  main.py
```

### 前端结构

```text
frontend/
  src/
    components/    — products/, knowledge/, tickets/, chat/, common/
    services/      — products.ts, knowledge.ts, tickets.ts, chat.ts, http.ts, system.ts
    stores/        — products.ts, knowledge.ts, tickets.ts, chat.ts, system.ts
    types/         — product.ts, knowledge.ts, ticket.ts, chat.ts, index.ts
    App.vue        — 客服场景三栏布局
    main.ts
```

---

## 6. 数据模型

### 核心业务模型

| 模型 | 说明 |
|------|------|
| Product | 产品（name, category, version, status） |
| ProductManual | 产品手册（替代原 Document） |
| ProductSpec | 产品参数/规格 |
| FaultSOP | 故障排查 SOP（含 symptoms/steps JSON） |
| Ticket | 工单（含状态流转：open→in_progress→resolved→closed） |

### 基础设施模型

| 模型 | 说明 |
|------|------|
| Chunk | 文档切片（新增 product_id, source_category） |
| Session | 会话（新增 product_id, ticket_id） |
| Message | 消息（新增 diagnosis_context） |
| Task | 异步任务 |

### 文档状态机

- UPLOADED → PARSING → CHUNKING → EMBEDDING → READY
- 任何阶段可进入 FAILED

### 工单状态机

- open → in_progress → resolved → closed

---

## 7. 模块职责划分

- `api`：只负责接口协议、参数校验、返回格式
- `orchestrators`：负责流程编排，不承担底层细节实现
- `services`：负责领域逻辑
- `repositories`：负责数据访问
- `tasks`：负责后台任务定义与调度入口
- `tools`：客服专用 Tool Calling（product_spec_lookup, ticket_search, fault_diagnosis, sop_lookup）
- `infrastructure`：负责外部系统接入与适配

---

## 8. 开发规范

### 命名规范
- 命名必须语义化
- 文件名优先使用小写英文加下划线
- 避免无意义命名

### 单一职责
- 每个文件只承担一个主要责任
- 每个类只围绕一个核心对象或行为
- 每个函数只完成一个清晰动作

### KISS / DRY
- 优先最简单可运行方案
- 不为未来可能用到的能力做超前抽象
- 可复用逻辑应抽取，禁止复制粘贴

### 错误处理
- 不允许吞掉异常
- 所有关键失败都要有明确错误链路
- SOP 匹配失败降级为通用检索
- LLM 失败返回检索原文
- 工单匹配无结果自动创建新工单

### 测试规范
- 核心逻辑必须有单元测试
- 接口与数据库交互必须有集成测试
- 至少保留一条主链路测试
- 失败路径和降级路径必须测试

---

## 9. 默认决策顺序

1. 先设计清楚，再写代码
2. FastAPI 优先于继续扩展 Streamlit
3. PostgreSQL + pgvector 优先于新增独立向量库
4. RQ 优先于 Celery
5. SSE 优先于 WebSocket
6. 渐进迁移优先于推倒重写
7. 小步迭代优先于一次性大改

---

## 10. 文档同步规则

当架构、技术栈、阶段路线、目录结构发生变化时，必须同步更新：
- `CLAUDE.md`
- `docs/superpowers/specs/` 下的设计文档
- `docs/superpowers/plans/` 下的实施计划

如果实现与文档发生偏离，优先修正文档或回退实现方向。
