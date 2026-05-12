from __future__ import annotations

from dataclasses import dataclass


SCRIPT_CATEGORY_SOOTHE = "soothe"
SCRIPT_CATEGORY_EXPLAIN = "explain"
SCRIPT_CATEGORY_GUIDE = "guide"
SCRIPT_CATEGORY_CONFIRM = "confirm"

SCRIPT_PROMPT = (
    "你是一位客服话术推荐助手。根据用户的问题和已有的回答引用信息，"
    "生成推荐的客服话术建议。\n\n"
    "话术类别说明：\n"
    "- soothe（安抚）：用于缓解用户焦虑、表达理解和共情\n"
    "- explain（解释）：用于清晰解释问题原因、技术细节\n"
    "- guide（引导）：用于引导用户进行操作、排查步骤\n"
    "- confirm（确认）：用于确认用户问题、核实关键信息\n\n"
    "请按 JSON 数组格式返回，每个元素包含 category 和 content 两个字段。"
    "例如：\n"
    '[{"category": "soothe", "content": "我理解您遇到的困扰，我们会尽快帮您解决。"}]\n\n'
    "只返回 JSON 数组，不要返回其他内容。"
)


@dataclass(frozen=True)
class ScriptSuggestion:
    category: str
    content: str


class ScriptRecommendService:
    def __init__(self, *, chat_client: object) -> None:
        self.chat_client = chat_client

    def recommend(self, *, query: str, citations: list | None = None) -> list[ScriptSuggestion]:
        user_prompt = f"用户问题：{query}"
        if citations:
            citation_texts: list[str] = []
            for index, citation in enumerate(citations, start=1):
                if isinstance(citation, dict):
                    content = citation.get("content", "")
                    document_name = citation.get("document_name", "未知文档")
                else:
                    content = getattr(citation, "content", "")
                    document_name = getattr(citation, "document_name", "未知文档")
                citation_texts.append(f"[{index}] {document_name}：{content}")
            user_prompt += f"\n\n引用信息：\n" + "\n".join(citation_texts)

        response = self.chat_client.generate(
            system_prompt=SCRIPT_PROMPT,
            user_prompt=user_prompt,
        )

        return self._parse_response(response)

    def _parse_response(self, response: str) -> list[ScriptSuggestion]:
        import json

        cleaned = response.strip()
        if cleaned.startswith("```"):
            first_newline = cleaned.find("\n")
            if first_newline != -1:
                cleaned = cleaned[first_newline + 1:]
            last_backticks = cleaned.rfind("```")
            if last_backticks != -1:
                cleaned = cleaned[:last_backticks]
            cleaned = cleaned.strip()

        try:
            items = json.loads(cleaned)
        except json.JSONDecodeError:
            return []

        if not isinstance(items, list):
            return []

        valid_categories = {SCRIPT_CATEGORY_SOOTHE, SCRIPT_CATEGORY_EXPLAIN, SCRIPT_CATEGORY_GUIDE, SCRIPT_CATEGORY_CONFIRM}
        suggestions: list[ScriptSuggestion] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            category = item.get("category", "")
            content = item.get("content", "")
            if category in valid_categories and content:
                suggestions.append(ScriptSuggestion(category=category, content=content))

        return suggestions
