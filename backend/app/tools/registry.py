from __future__ import annotations

from backend.app.exceptions import AppError
from backend.app.tools.base import ToolDefinition
from backend.app.tools.fault_diagnosis import FaultDiagnosisTool
from backend.app.tools.product_spec_lookup import ProductSpecLookupTool
from backend.app.tools.sop_lookup import SOPLookupTool
from backend.app.tools.ticket_search import TicketSearchTool


class ToolRegistry:
    def __init__(self) -> None:
        self._definitions: dict[str, ToolDefinition] = {}

    def register(self, definition: ToolDefinition) -> None:
        self._definitions[definition.name] = definition

    def get(self, name: str) -> ToolDefinition:
        definition = self._definitions.get(name)
        if definition is None:
            raise AppError("工具未注册", code="tool_not_registered", status_code=400)
        return definition

    def list_schemas(self, names: list[str] | None = None) -> list[dict[str, object]]:
        if names is None:
            definitions = self._definitions.values()
        else:
            definitions = [self.get(name) for name in names]
        return [definition.to_schema() for definition in definitions]


_DEFAULT_TOOL_CLASSES = [
    ProductSpecLookupTool,
    TicketSearchTool,
    FaultDiagnosisTool,
    SOPLookupTool,
]


def create_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    for tool_cls in _DEFAULT_TOOL_CLASSES:
        registry.register(tool_cls.definition())
    return registry
