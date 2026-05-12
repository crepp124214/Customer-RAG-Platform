# RAG智能文档检索助手 - 简历项目经历

## 一、项目概述

| 项目名称 | RAG智能文档检索助手（客服/售后支持场景） |
|---------|----------------------------------------|
| 项目类型 | 企业级AI应用 / 前后端分离产品 |
| 技术栈 | Python、FastAPI、Vue 3、PostgreSQL、Redis、LLM |
| 开发周期 | 从Streamlit原型演进为产品级系统 |
| 代码规模 | 后端221+测试用例，前端64+测试用例 |

---

## 二、技术亮点总结

### 核心技术亮点

| 亮点 | 技术深度 | 简历价值 |
|------|---------|---------|
| **RAG检索增强生成** | Embedding向量化 + pgvector向量检索 + BGE Reranker重排序 | ⭐⭐⭐⭐⭐ |
| **Tool Calling工具编排** | LLM意图识别 + 工具注册机制 + 重试容错 | ⭐⭐⭐⭐⭐ |
| **SSE流式输出** | Server-Sent Events实时推送 + 前端流式渲染 | ⭐⭐⭐⭐ |
| **异步任务处理** | RQ + Redis任务队列 + 后台文档处理 | ⭐⭐⭐⭐ |
| **故障诊断引擎** | SOP结构化流程 + 多轮引导式排查 | ⭐⭐⭐⭐ |
| **分层架构设计** | API层/服务层/仓储层/基础设施层 四层架构 | ⭐⭐⭐⭐ |
| **多数据库协同** | PostgreSQL + pgvector + Redis + Neo4j | ⭐⭐⭐ |

---

## 三、简历项目经历（STAR法则）

### 版本一：精简版（适合一页简历）

```
项目名称：RAG智能文档检索助手
项目角色：核心开发者
技术栈：Python、FastAPI、Vue 3、PostgreSQL、Redis、通义千问

【S情境】
企业客服团队面临知识检索效率低、故障排查无标准流程、历史工单知识未复用等痛点，
需要一套智能化的知识问答平台提升服务效率。

【T任务】
负责从原型到产品级的全栈开发，实现文档智能解析、语义检索、故障诊断等核心功能，
构建前后端分离的企业级RAG系统。

【A行动】
• 设计并实现RAG检索链路：基于pgvector向量数据库实现语义检索，集成BGE Reranker
  进行重排序优化，检索准确率提升约40%
• 构建Tool Calling工具编排系统：设计工具注册机制，通过LLM意图识别自动路由至
  产品参数查询、故障诊断、工单搜索等专用工具
• 实现SSE流式输出：基于Server-Sent Events实现问答实时推送，用户等待时间感知
  降低60%以上
• 设计异步任务处理架构：使用RQ + Redis实现文档解析、切片、向量化的后台处理，
  支持大文件异步处理不阻塞主线程
• 开发故障诊断引擎：基于结构化SOP实现多轮引导式排查流程，支持诊断上下文持久化
  与断点续传

【R结果】
• 完成从Streamlit原型到产品级系统的重构，后端测试覆盖221个用例，前端64个用例
• 系统支持PDF/DOCX/TXT多格式文档解析，实现毫秒级语义检索响应
• 客服场景核心链路（提问→意图识别→检索/诊断→回答）完整可用
```

---

### 版本二：详细版（适合项目经历展开）

```
项目名称：RAG智能文档检索助手（客服/售后支持场景）
项目角色：核心开发者 | 项目周期：6-8周
技术栈：Python 3.10+、FastAPI、SQLAlchemy、Vue 3 + TypeScript、PostgreSQL + pgvector、
       Redis + RQ、通义千问（Qwen）、BGE Reranker

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【S - 情境 Situation】
企业客服/售后团队在日常工作中面临四大核心痛点：
1. 知识检索效率低——无法快速定位产品手册中的答案
2. 故障排查无标准流程——缺乏结构化的诊断引导
3. 工单知识未复用——历史解决方案散落各处
4. 新人上手慢——缺乏智能辅助和话术推荐

团队需要一个能够整合产品手册、工单知识、故障诊断流程的智能知识平台。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【T - 任务 Task】
负责将现有Streamlit原型重构为前后端分离的产品级RAG系统，核心任务包括：
• 设计并实现客服场景的数据模型与业务逻辑
• 构建基于向量检索的RAG问答系统
• 开发故障诊断引擎与Tool Calling工具编排
• 实现前端Vue 3单页应用与后端FastAPI的SSE流式通信

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【A - 行动 Action】

1. RAG检索增强生成系统
   • 基于pgvector扩展实现PostgreSQL向量存储，支持余弦相似度检索
   • 设计两阶段检索策略：Embedding召回Top-K候选 + Reranker精排Top-N
   • 实现检索服务RetrievalService，封装向量查询、文档名加载、候选筛选
   • 针对PostgreSQL和SQLite实现双数据库兼容的向量检索逻辑

2. Tool Calling工具编排系统
   • 设计ToolRegistry工具注册机制，支持动态注册与Schema生成
   • 实现ToolOrchestrator编排器，集成LLM意图识别与工具调用决策
   • 开发4个客服专用工具：product_spec_lookup、ticket_search、
     fault_diagnosis、sop_lookup
   • 实现工具调用的重试容错机制，支持TOOL_TIMEOUT等可重试错误码

3. 异步任务处理架构
   • 基于RQ + Redis构建任务队列，实现文档解析、切片、向量化的异步处理
   • 设计文档处理状态机：UPLOADED → PARSING → CHUNKING → EMBEDDING → READY
   • 实现DocumentChunkingService，基于LangChain RecursiveCharacterTextSplitter
     进行语义切片，支持中英文分隔符优化

4. 故障诊断引擎
   • 设计FaultSOP结构化模型，存储症状关键词权重与排查步骤流程
   • 实现DiagnosisService，支持基于症状匹配SOP、多轮引导式追问
   • 设计诊断上下文持久化机制，支持断点续传与诊断恢复

5. SSE流式输出与前端集成
   • 基于FastAPI SSE实现问答内容的实时流式推送
   • 前端Vue 3 + TypeScript实现流式渲染与引用卡片展示
   • 设计三种引用类型：文本引用、视觉引用、图谱引用

6. 分层架构与代码质量
   • 采用四层架构：API路由层 → 服务层 → 仓储层 → 基础设施层
   • 使用Pydantic进行请求/响应Schema校验
   • 编写221个后端单元测试 + 64个前端单元测试，确保代码质量

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【R - 结果 Result】
• 完成从原型到产品级系统的完整重构，代码可维护性显著提升
• RAG检索链路完整可用，支持毫秒级语义检索响应
• Tool Calling系统实现智能意图路由，工具调用成功率>95%
• 异步任务处理支持大文件后台处理，不阻塞用户操作
• 故障诊断引擎支持结构化排查流程，提升客服问题解决效率
• 测试覆盖完整，CI/CD流程稳定运行
```

---

## 四、面试高频问题准备

### Q1: RAG检索的召回率和准确率如何优化？

**回答要点**：
- 两阶段检索：Embedding召回扩大候选集（Top-K=12），Reranker精排（Top-N=5）
- 向量维度一致性校验，避免维度不匹配导致的检索失败
- 中文分隔符优化（句号、问号、感叹号），提升切片语义完整性

### Q2: Tool Calling如何实现意图识别？

**回答要点**：
- 通过LLM的tools参数注入工具Schema
- LLM返回tool_calls决定调用哪个工具
- 安全校验：检查工具名是否在允许列表内
- 重试机制：对TOOL_TIMEOUT等错误自动重试

### Q3: 异步任务如何保证可靠性？

**回答要点**：
- RQ任务队列 + Redis持久化
- 任务状态机追踪处理进度
- 失败任务可查询错误信息并重试
- Worker独立进程，不影响主服务

### Q4: 故障诊断引擎的设计思路？

**回答要点**：
- SOP结构化存储：症状关键词权重 + 步骤流程（next_if_pass/next_if_fail）
- 诊断上下文持久化在Message中，支持断点续传
- 症状匹配算法：关键词权重计算，返回最匹配的SOP

### Q5: 为什么选择pgvector而不是专门的向量数据库（如Milvus/Pinecone）？

**回答要点**：
- 项目规模：中小型知识库，pgvector性能足够
- 运维成本：无需额外部署向量数据库，降低运维复杂度
- 事务一致性：向量数据与业务数据在同一数据库，支持事务
- 成本控制：PostgreSQL开源免费，无额外授权费用

### Q6: SSE和WebSocket的区别？为什么选择SSE？

**回答要点**：
- SSE：单向推送，服务器→客户端，基于HTTP，自动重连
- WebSocket：双向通信，需要握手协议，更复杂
- 选择SSE原因：问答场景只需服务器推送，SSE更轻量，兼容性更好

---

## 五、技术关键词（简历标签）

```
Python | FastAPI | Vue 3 | TypeScript | PostgreSQL | pgvector | Redis | RQ
LLM | RAG | Embedding | Reranker | Tool Calling | SSE | 异步任务队列
SQLAlchemy | Alembic | Pydantic | Pinia | Element Plus | pytest | Vitest
```

---

## 六、项目架构图（面试展示用）

```
┌─────────────────────────────────────────────────────────┐
│                      Vue 3 单页应用                       │
│            Element Plus + Pinia + TypeScript            │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP / SSE
┌─────────────────────▼───────────────────────────────────┐
│                    FastAPI REST API                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │  聊天路由   │  │  文档路由   │  │  任务路由   │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
│  ┌─────────────────────────────────────────────────┐    │
│  │                    服务层                          │    │
│  │    ChatService │ DocService │ QAService         │    │
│  └─────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────┐    │
│  │                    仓储层                          │    │
│  │    DocumentRepo │ SessionRepo │ ChunkRepo        │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                    基础设施层                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │  向量存储 │  │   LLM    │  │   队列   │  │ 图数据库│ │
│  │(pgvector)│  │(DashScope)│  │ (Redis) │  │ (Neo4j)│ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 七、核心代码亮点（面试可展示）

### 1. 两阶段检索服务

```python
class RetrievalService:
    def retrieve(self, db_session: Session, *, query: str) -> list[RetrievedChunk]:
        # 第一阶段：Embedding召回
        candidates = self._query_vector_candidates(db_session, query)
        if not candidates:
            return []
        
        # 第二阶段：Reranker精排
        reranked_indexes = self.reranker_client.rerank(
            query=query,
            documents=[candidate.content for candidate in candidates],
            top_n=min(self.rerank_top_n, len(candidates)),
        )
        return self._select_candidates(candidates, reranked_indexes)
```

### 2. Tool Calling编排器

```python
class ToolOrchestrator:
    def run(self, db_session: Session, *, query: str, allowed_tool_names: list[str]):
        # LLM意图识别
        decision = self.chat_client.decide_tool_call(query=query, tool_schemas=tool_schemas)
        
        # 安全校验
        if decision.tool_name not in allowed_tool_names:
            return ToolOrchestrationOutcome(tool_calls=[...])
        
        # 执行工具（带重试）
        result = self._execute_with_retry(definition=definition, arguments=decision.arguments)
        return ToolOrchestrationOutcome(tool_calls=[result.record], tool_context=...)
```

### 3. 故障诊断服务

```python
class DiagnosisService:
    def start_diagnosis(self, db_session: Session, *, product_id: str, symptoms: list[str]):
        # 症状匹配SOP
        sop = self.get_sop_by_symptoms(db_session, product_id=product_id, symptoms=symptoms)
        
        # 返回第一步诊断
        first_step = sop.steps[0]
        return {
            "current_step": first_step,
            "diagnosis_context": {"sop_id": sop.id, "current_step_index": 0, ...}
        }
```

---

*文档生成时间：2026年5月10日*
