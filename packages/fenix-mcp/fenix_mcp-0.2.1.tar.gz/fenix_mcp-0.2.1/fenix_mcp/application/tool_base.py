# SPDX-License-Identifier: MIT
"""Base abstractions for MCP tools."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Type

from pydantic import BaseModel, ConfigDict

from fenix_mcp.infrastructure.context import AppContext


class ToolRequest(BaseModel):
    """Base request payload."""

    model_config = ConfigDict(extra="forbid")


ToolResponse = Dict[str, Any]


class Tool(ABC):
    """Interface implemented by all tools."""

    name: str
    description: str
    request_model: Type[ToolRequest] = ToolRequest

    def schema(self) -> Dict[str, Any]:
        """Return JSON schema describing the tool arguments."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.request_model.model_json_schema(),
        }

    async def execute(
        self, raw_arguments: Dict[str, Any], context: AppContext
    ) -> ToolResponse:
        """Validate raw arguments and run the tool."""
        payload = self.request_model.model_validate(raw_arguments or {})
        return await self.run(payload, context)

    @abstractmethod
    async def run(self, payload: ToolRequest, context: AppContext) -> ToolResponse:
        """Execute business logic and return a MCP-formatted response."""
