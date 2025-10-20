# SPDX-License-Identifier: MIT
"""Domain helpers for intelligence (memory) operations."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from fenix_mcp.infrastructure.fenix_api.client import FenixApiClient


@dataclass(slots=True)
class IntelligenceService:
    api: FenixApiClient
    logger: Any

    async def smart_create_memory(
        self,
        *,
        title: str,
        content: str,
        context: Optional[str],
        source: Optional[str],
        importance: str,
        tags: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:
        metadata_parts: List[str] = []
        if context:
            metadata_parts.append(f"Contexto: {context}")
        if source:
            metadata_parts.append(f"Fonte: {source}")

        payload = {
            "title": title,
            "content": content,
            "metadata": "\n".join(metadata_parts) if metadata_parts else None,
            "priority_score": _importance_to_priority(importance),
            "tags": list(tags) if tags else None,
        }
        return await self._call(self.api.smart_create_memory, _strip_none(payload))

    async def query_memories(self, **filters: Any) -> List[Dict[str, Any]]:
        params = _strip_none(filters)
        include_content = bool(params.pop("content", True))
        include_metadata = bool(params.pop("metadata", False))
        return (
            await self._call(
                self.api.list_memories,
                include_content=include_content,
                include_metadata=include_metadata,
                **params,
            )
            or []
        )

    async def similar_memories(
        self, *, content: str, threshold: float, max_results: int
    ) -> List[Dict[str, Any]]:
        payload = {
            "content": content,
            "threshold": threshold,
        }
        result = (
            await self._call(self.api.find_similar_memories, _strip_none(payload)) or []
        )
        if isinstance(result, list) and max_results:
            return result[:max_results]
        return result

    async def consolidate_memories(
        self, *, memory_ids: Iterable[str], strategy: str
    ) -> Dict[str, Any]:
        payload = {
            "memoryIds": list(memory_ids),
            "strategy": strategy,
        }
        return await self._call(self.api.consolidate_memories, payload)

    async def priority_memories(self, *, limit: int) -> List[Dict[str, Any]]:
        params = {
            "limit": limit,
            "sortBy": "priority_score",
            "sortOrder": "desc",
        }
        return (
            await self._call(
                self.api.list_memories,
                include_content=False,
                include_metadata=False,
                **params,
            )
            or []
        )

    async def analytics(self, *, time_range: str, group_by: str) -> Dict[str, Any]:
        memories = await self.query_memories(
            limit=200, timeRange=time_range, groupBy=group_by
        )
        summary: Dict[str, Any] = {
            "total_memories": len(memories),
            "by_group": {},
        }
        group_key = group_by
        for memory in memories:
            key = memory.get(group_key) or memory.get("metadata") or "N/A"
            summary["by_group"][key] = summary["by_group"].get(key, 0) + 1
        return summary

    async def update_memory(self, memory_id: str, **fields: Any) -> Dict[str, Any]:
        payload = _strip_none(fields)
        if "importance" in payload:
            payload["priority_score"] = _importance_to_priority(
                payload.pop("importance")
            )
        mapping = {
            "documentation_item_id": "documentationItemId",
            "mode_id": "modeId",
            "rule_id": "ruleId",
            "work_item_id": "workItemId",
            "sprint_id": "sprintId",
        }
        for old_key, new_key in mapping.items():
            if old_key in payload:
                payload[new_key] = payload.pop(old_key)
        return await self._call(self.api.update_memory, memory_id, payload)

    async def _call(self, func, *args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)


def _importance_to_priority(importance: Optional[str]) -> float:
    mapping = {
        "low": 0.2,
        "medium": 0.5,
        "high": 0.7,
        "critical": 0.9,
    }
    if importance is None:
        return 0.5
    return mapping.get(importance.lower(), 0.5)


def _strip_none(data: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in data.items() if value not in (None, "")}
