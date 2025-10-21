# SPDX-License-Identifier: MIT
"""Intelligence tool implementation (memories and smart operations)."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator

from fenix_mcp.application.presenters import text
from fenix_mcp.application.tool_base import Tool, ToolRequest
from fenix_mcp.domain.intelligence import IntelligenceService, build_metadata
from fenix_mcp.infrastructure.context import AppContext


class IntelligenceAction(str, Enum):
    def __new__(cls, value: str, description: str):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    SMART_CREATE = (
        "memory_smart_create",
        "Cria memórias inteligentes com análise de similaridade.",
    )
    QUERY = ("memory_query", "Lista memórias aplicando filtros e busca textual.")
    SIMILARITY = ("memory_similarity", "Busca memórias similares a um conteúdo base.")
    CONSOLIDATE = (
        "memory_consolidate",
        "Consolida múltiplas memórias em uma principal.",
    )
    PRIORITY = ("memory_priority", "Retorna memórias ordenadas por prioridade.")
    ANALYTICS = ("memory_analytics", "Calcula métricas e analytics das memórias.")
    UPDATE = ("memory_update", "Atualiza campos de uma memória existente.")
    HELP = ("memory_help", "Mostra as ações suportadas e seus usos.")

    @classmethod
    def choices(cls) -> List[str]:
        return [member.value for member in cls]

    @classmethod
    def formatted_help(cls) -> str:
        lines = [
            "| **Ação** | **Descrição** |",
            "| --- | --- |",
        ]
        for member in cls:
            lines.append(f"| `{member.value}` | {member.description} |")
        return "\n".join(lines)


ACTION_FIELD_DESCRIPTION = (
    "Ação de inteligência a executar. Use um dos valores: "
    + ", ".join(
        f"`{member.value}` ({member.description.rstrip('.')})."
        for member in IntelligenceAction
    )
)


class IntelligenceRequest(ToolRequest):
    action: IntelligenceAction = Field(description=ACTION_FIELD_DESCRIPTION)
    title: Optional[str] = Field(default=None, description="Título da memória.")
    content: Optional[str] = Field(
        default=None, description="Conteúdo/texto da memória."
    )
    metadata: Optional[str] = Field(
        default=None,
        description="Metadata estruturada da memória (formato pipe, toml compacto, etc.).",
    )
    context: Optional[str] = Field(default=None, description="Contexto adicional.")
    source: Optional[str] = Field(default=None, description="Fonte da memória.")
    importance: Optional[str] = Field(
        default=None, description="Nível de importância da memória."
    )
    include_content: bool = Field(
        default=False,
        description="Retornar conteúdo completo das memórias? Defina true para incluir o texto integral.",
    )
    include_metadata: bool = Field(
        default=False,
        description="Retornar metadata completa das memórias? Defina true para incluir o campo bruto.",
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="Tags da memória como array JSON de strings.",
        json_schema_extra={"example": ["tag1", "tag2", "tag3"]},
    )

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v: Any) -> Optional[List[str]]:
        """Validate and normalize tags field."""
        if v is None or v == "":
            return None

        # If it's already a list, return as is
        if isinstance(v, (list, tuple, set)):
            return [str(item).strip() for item in v if str(item).strip()]

        # If it's a string, try to parse as JSON
        if isinstance(v, str):
            try:
                import json

                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except (json.JSONDecodeError, TypeError):
                pass

            # If JSON parsing fails, treat as comma-separated string
            return [item.strip() for item in v.split(",") if item.strip()]

        # For any other type, convert to string and wrap in list
        return [str(v).strip()] if str(v).strip() else None

    limit: int = Field(default=20, ge=1, le=100, description="Limite de resultados.")
    offset: int = Field(default=0, ge=0, description="Offset para paginação.")
    query: Optional[str] = Field(default=None, description="Termo de busca.")
    category: Optional[str] = Field(default=None, description="Categoria para filtro.")
    date_from: Optional[str] = Field(default=None, description="Filtro inicial (ISO).")
    date_to: Optional[str] = Field(default=None, description="Filtro final (ISO).")
    threshold: float = Field(
        default=0.8, ge=0, le=1, description="Limite mínimo de similaridade."
    )
    max_results: int = Field(
        default=5, ge=1, le=20, description="Máximo de memórias similares."
    )
    memory_ids: Optional[List[str]] = Field(
        default=None, description="IDs para consolidação."
    )
    strategy: str = Field(default="merge", description="Estratégia de consolidação.")
    time_range: str = Field(
        default="month", description="Janela de tempo para analytics."
    )
    group_by: str = Field(default="category", description="Agrupamento para analytics.")
    id: Optional[str] = Field(default=None, description="ID da memória para update.")
    documentation_item_id: Optional[str] = Field(
        default=None, description="ID de documentação relacionada."
    )
    mode_id: Optional[str] = Field(default=None, description="ID do modo relacionado.")
    rule_id: Optional[str] = Field(default=None, description="ID da regra relacionada.")
    work_item_id: Optional[str] = Field(
        default=None, description="ID do work item relacionado."
    )
    sprint_id: Optional[str] = Field(
        default=None, description="ID do sprint relacionado."
    )


class IntelligenceTool(Tool):
    name = "intelligence"
    description = (
        "Operações de inteligência do Fênix Cloud (memórias e smart operations)."
    )
    request_model = IntelligenceRequest

    def __init__(self, context: AppContext):
        self._context = context
        self._service = IntelligenceService(context.api_client, context.logger)

    async def run(self, payload: IntelligenceRequest, context: AppContext):
        action = payload.action
        if action is IntelligenceAction.HELP:
            return await self._handle_help()
        if action is IntelligenceAction.SMART_CREATE:
            return await self._handle_smart_create(payload)
        if action is IntelligenceAction.QUERY:
            return await self._handle_query(payload)
        if action is IntelligenceAction.SIMILARITY:
            return await self._handle_similarity(payload)
        if action is IntelligenceAction.CONSOLIDATE:
            return await self._handle_consolidate(payload)
        if action is IntelligenceAction.PRIORITY:
            return await self._handle_priority(payload)
        if action is IntelligenceAction.ANALYTICS:
            return await self._handle_analytics(payload)
        if action is IntelligenceAction.UPDATE:
            return await self._handle_update(payload)
        return text(
            "❌ Ação inválida para intelligence.\n\nEscolha um dos valores:\n"
            + "\n".join(f"- `{value}`" for value in IntelligenceAction.choices())
        )

    async def _handle_smart_create(self, payload: IntelligenceRequest):
        if not payload.title or not payload.content:
            return text("❌ Informe título e conteúdo para criar uma memória.")

        if not payload.metadata or not payload.metadata.strip():
            return text("❌ Informe metadata para criar uma memória.")

        if not payload.source or not payload.source.strip():
            return text("❌ Informe source para criar uma memória.")

        try:
            normalized_tags = _ensure_tag_sequence(payload.tags)
        except ValueError as exc:
            return text(f"❌ {exc}")

        if not normalized_tags or len(normalized_tags) == 0:
            return text("❌ Informe tags para criar uma memória.")

        memory = await self._service.smart_create_memory(
            title=payload.title,
            content=payload.content,
            metadata=payload.metadata,
            context=payload.context,
            source=payload.source,
            importance=payload.importance,
            tags=normalized_tags,
        )
        lines = [
            "🧠 **Memória criada com sucesso!**",
            f"ID: {memory.get('memoryId') or memory.get('id', 'N/A')}",
            f"Ação: {memory.get('action') or 'criado'}",
            f"Similaridade: {format_percentage(memory.get('similarity'))}",
            f"Tags: {', '.join(memory.get('tags', [])) or 'Automáticas'}",
            f"Categoria: {memory.get('category') or 'Automática'}",
        ]
        return text("\n".join(lines))

    async def _handle_query(self, payload: IntelligenceRequest):
        memories = await self._service.query_memories(
            limit=payload.limit,
            offset=payload.offset,
            query=payload.query,
            tags=payload.tags,
            include_content=payload.include_content,
            include_metadata=payload.include_metadata,
            modeId=payload.mode_id,
            ruleId=payload.rule_id,
            workItemId=payload.work_item_id,
            sprintId=payload.sprint_id,
            documentationItemId=payload.documentation_item_id,
            category=payload.category,
            dateFrom=payload.date_from,
            dateTo=payload.date_to,
            importance=payload.importance,
        )
        if not memories:
            return text("🧠 Nenhuma memória encontrada.")
        body = "\n\n".join(_format_memory(mem) for mem in memories)
        return text(f"🧠 **Memórias ({len(memories)}):**\n\n{body}")

    async def _handle_similarity(self, payload: IntelligenceRequest):
        if not payload.content:
            return text("❌ Informe o conteúdo base para comparar similitude.")
        memories = await self._service.similar_memories(
            content=payload.content,
            threshold=payload.threshold,
            max_results=payload.max_results,
        )
        if not memories:
            return text("🔍 Nenhuma memória similar encontrada.")
        body = "\n\n".join(
            f"🔍 **{mem.get('title', 'Sem título')}**\n   Similaridade: {format_percentage(mem.get('finalScore'))}\n   ID: {mem.get('memoryId', 'N/A')}"
            for mem in memories
        )
        return text(f"🔍 **Memórias similares ({len(memories)}):**\n\n{body}")

    async def _handle_consolidate(self, payload: IntelligenceRequest):
        if not payload.memory_ids or len(payload.memory_ids) < 2:
            return text("❌ Informe ao menos 2 IDs de memória para consolidar.")
        result = await self._service.consolidate_memories(
            memory_ids=payload.memory_ids,
            strategy=payload.strategy,
        )
        lines = [
            "🔄 **Consolidação concluída!**",
            f"Memória principal: {result.get('primary_memory_id', 'N/A')}",
            f"Consolidadas: {result.get('consolidated_count', 'N/A')}",
            f"Ação executada: {result.get('action', 'N/A')}",
        ]
        return text("\n".join(lines))

    async def _handle_priority(self, payload: IntelligenceRequest):
        memories = await self._service.priority_memories(limit=payload.limit)
        if not memories:
            return text("✅ Nenhuma memória prioritária no momento.")
        body = "\n\n".join(_format_memory(mem) for mem in memories)
        return text(f"🧠 **Memórias prioritárias ({len(memories)}):**\n\n{body}")

    async def _handle_analytics(self, payload: IntelligenceRequest):
        analytics = await self._service.analytics(
            time_range=payload.time_range,
            group_by=payload.group_by,
        )
        lines = [
            "📊 **Memória - Analytics**",
            f"Total: {analytics.get('total_memories', 0)}",
            f"Novas: {analytics.get('new_memories', 0)}",
            f"Mais acessada: {analytics.get('most_accessed', 'N/A')}",
            f"Acesso médio: {analytics.get('avg_access_count', 'N/A')}",
        ]
        by_group = analytics.get("by_group")
        if isinstance(by_group, dict):
            lines.append("\nPor grupo:")
            lines.extend(f"- {key}: {value}" for key, value in by_group.items())
        return text("\n".join(lines))

    async def _handle_update(self, payload: IntelligenceRequest):
        if not payload.id:
            return text("❌ Informe o ID da memória para atualização.")
        existing = await self._service.get_memory(
            payload.id, include_content=False, include_metadata=True
        )
        try:
            normalized_tags = _ensure_tag_sequence(payload.tags)
        except ValueError as exc:
            return text(f"❌ {exc}")
        metadata = build_metadata(
            payload.metadata,
            importance=payload.importance,
            tags=normalized_tags,
            source=payload.source,
            existing=existing.get("metadata") if isinstance(existing, dict) else None,
        )
        update_fields: Dict[str, Any] = {
            "title": payload.title,
            "content": payload.content,
            "metadata": metadata,
            "tags": normalized_tags,
            "documentation_item_id": payload.documentation_item_id,
            "mode_id": payload.mode_id,
            "rule_id": payload.rule_id,
            "work_item_id": payload.work_item_id,
            "sprint_id": payload.sprint_id,
            "importance": payload.importance,
        }
        memory = await self._service.update_memory(payload.id, **update_fields)
        return text(
            "\n".join(
                [
                    "✅ **Memória atualizada!**",
                    f"ID: {memory.get('id', payload.id)}",
                    f"Título: {memory.get('title', 'N/A')}",
                    f"Prioridade: {memory.get('priority_score', 'N/A')}",
                ]
            )
        )

    async def _handle_help(self):
        return text(
            "📚 **Ações disponíveis para intelligence**\n\n"
            + IntelligenceAction.formatted_help()
        )


def _format_memory(memory: Dict[str, Any]) -> str:
    return "\n".join(
        [
            f"🧠 **{memory.get('title', 'Sem título')}**",
            f"ID: {memory.get('id', memory.get('memoryId', 'N/A'))}",
            f"Categoria: {memory.get('category', 'N/A')}",
            f"Tags: {', '.join(memory.get('tags', [])) or 'Nenhuma'}",
            f"Importância: {memory.get('importance', 'N/A')}",
            f"Acessos: {memory.get('access_count', 'N/A')}",
        ]
    )


def format_percentage(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"{value * 100:.1f}%"


def _ensure_tag_sequence(raw: Optional[Any]) -> Optional[List[str]]:
    if raw is None or raw == "":
        return None
    if isinstance(raw, (list, tuple, set)):
        result = [str(item).strip() for item in raw if str(item).strip()]
        return result or None
    if isinstance(raw, str):
        # Try to parse as JSON array first
        try:
            import json

            parsed = json.loads(raw)
            if isinstance(parsed, list):
                result = [str(item).strip() for item in parsed if str(item).strip()]
                return result or None
        except (json.JSONDecodeError, TypeError):
            pass

        raise ValueError(
            "O campo `tags` deve ser enviado como array JSON, por exemplo: "
            '["tag1", "tag2"].'
        )
    return [str(raw).strip()]
