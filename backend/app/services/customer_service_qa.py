from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from backend.app.exceptions import AppError
from backend.app.models.message import Message
from backend.app.repositories.message_repository import MessageRepository
from backend.app.services.diagnosis_service import DiagnosisService
from backend.app.services.retrieval_service import RetrievedChunk
from backend.app.services.ticket_service import TicketService


INTENT_KNOWLEDGE_QUERY = "knowledge_query"
INTENT_FAULT_DIAGNOSIS = "fault_diagnosis"
INTENT_TICKET_QUERY = "ticket_query"

CUSTOMER_SERVICE_SYSTEM_PROMPT = (
    "你是一位专业的客服智能助手。你的职责是：\n"
    "1. 以专业、同理心的态度回答用户问题\n"
    "2. 基于提供的知识库内容、诊断流程或历史工单给出准确回答\n"
    "3. 引用信息来源，让用户了解答案依据\n"
    "4. 当信息不足时，坦诚告知并建议用户补充细节\n"
    "5. 使用清晰易懂的语言，避免过度技术化\n\n"
    "回答规范：\n"
    "- 先给出直接回答，再补充细节\n"
    "- 引用来源时标注 [来源编号]\n"
    "- 涉及故障诊断时，引导用户按步骤排查\n"
    "- 语气友好专业，体现对用户问题的重视"
)

INTENT_DECISION_PROMPT = (
    "你是一个意图识别助手。根据用户的问题，判断应该使用哪种工具来回答。\n\n"
    "可选意图：\n"
    "1. knowledge_query - 用户在询问产品知识、使用方法、参数规格等文档相关问题\n"
    "2. fault_diagnosis - 用户描述了设备故障、异常现象，需要按诊断流程排查\n"
    "3. ticket_query - 用户想查询历史工单、类似问题处理记录\n\n"
    "请只返回意图名称，不要返回其他内容。如果无法判断，返回 knowledge_query。"
)


@dataclass(frozen=True)
class QAResult:
    answer: str
    intent: str
    citations: list[RetrievedChunk]
    diagnosis: dict[str, Any] | None
    similar_tickets: list[dict[str, Any]] | None


class CustomerServiceQA:
    def __init__(
        self,
        *,
        retrieval_service: object,
        diagnosis_service: DiagnosisService,
        ticket_service: TicketService,
        chat_client: object,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.diagnosis_service = diagnosis_service
        self.ticket_service = ticket_service
        self.chat_client = chat_client

    def answer(
        self,
        db_session: Session,
        *,
        query: str,
        session_id: str,
        product_id: str | None = None,
    ) -> QAResult:
        intent = self._recognize_intent(query)

        citations: list[RetrievedChunk] = []
        diagnosis_result: dict[str, Any] | None = None
        similar_tickets: list[dict[str, Any]] | None = None

        if intent == INTENT_KNOWLEDGE_QUERY:
            citations = self.retrieval_service.retrieve(db_session, query=query)

        elif intent == INTENT_FAULT_DIAGNOSIS:
            symptoms = self._extract_symptoms(query)
            try:
                diagnosis_result = self.diagnosis_service.start_diagnosis(
                    db_session,
                    product_id=product_id or "",
                    symptoms=symptoms,
                )
            except AppError:
                citations = self.retrieval_service.retrieve(db_session, query=query)
                diagnosis_result = None

        elif intent == INTENT_TICKET_QUERY:
            similar_tickets_raw = self.ticket_service.search_similar_tickets(
                db_session,
                query=query,
                product_id=product_id,
            )
            similar_tickets = [
                {
                    "id": t.id,
                    "title": t.title,
                    "status": t.status,
                    "priority": t.priority,
                    "solution": t.solution,
                }
                for t in similar_tickets_raw
            ]

        user_prompt = self._build_user_prompt(
            query=query,
            intent=intent,
            citations=citations,
            diagnosis_result=diagnosis_result,
            similar_tickets=similar_tickets,
        )

        answer = self.chat_client.generate(
            system_prompt=CUSTOMER_SERVICE_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        return QAResult(
            answer=answer,
            intent=intent,
            citations=citations,
            diagnosis=diagnosis_result,
            similar_tickets=similar_tickets,
        )

    def _recognize_intent(self, query: str) -> str:
        tool_schemas = [
            {
                "name": "intent_recognition",
                "description": "识别用户问题的意图类型",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "intent": {
                            "type": "string",
                            "enum": [INTENT_KNOWLEDGE_QUERY, INTENT_FAULT_DIAGNOSIS, INTENT_TICKET_QUERY],
                        }
                    },
                    "required": ["intent"],
                },
            }
        ]

        decision = self.chat_client.decide_tool_call(query=query, tool_schemas=tool_schemas)
        if decision is not None and decision.tool_name == "intent_recognition":
            intent = decision.arguments.get("intent", INTENT_KNOWLEDGE_QUERY)
            if intent in (INTENT_KNOWLEDGE_QUERY, INTENT_FAULT_DIAGNOSIS, INTENT_TICKET_QUERY):
                return intent

        return INTENT_KNOWLEDGE_QUERY

    def _extract_symptoms(self, query: str) -> list[str]:
        return [query]

    def _build_user_prompt(
        self,
        *,
        query: str,
        intent: str,
        citations: list[RetrievedChunk],
        diagnosis_result: dict[str, Any] | None,
        similar_tickets: list[dict[str, Any]] | None,
    ) -> str:
        parts = [f"用户问题：{query}"]
        parts.append(f"识别意图：{intent}")

        if citations:
            context_lines: list[str] = []
            for index, citation in enumerate(citations, start=1):
                location = f"第 {citation.page_number} 页" if citation.page_number is not None else "页码未知"
                context_lines.append(
                    f"[{index}] 文档：{citation.document_name}；位置：{location}；内容：{citation.content}"
                )
            parts.append(f"知识库参考：\n" + "\n".join(context_lines))

        if diagnosis_result is not None:
            step = diagnosis_result.get("current_step", {})
            parts.append(
                f"故障诊断流程：\n"
                f"- 诊断流程ID：{diagnosis_result.get('sop_id')}\n"
                f"- 当前步骤：{step.get('description', '未知')}\n"
                f"- 步骤进度：{diagnosis_result.get('current_step_index', 0) + 1}/{diagnosis_result.get('total_steps', 0)}"
            )

        if similar_tickets:
            ticket_lines: list[str] = []
            for index, ticket in enumerate(similar_tickets, start=1):
                ticket_lines.append(
                    f"[{index}] 标题：{ticket['title']}；状态：{ticket['status']}；解决方案：{ticket.get('solution', '暂无')}"
                )
            parts.append("相似历史工单：\n" + "\n".join(ticket_lines))

        return "\n\n".join(parts)
