# SPDX-License-Identifier: MIT
"""Productivity tool implementation (TODO operations)."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from fenix_mcp.application.presenters import text
from fenix_mcp.application.tool_base import Tool, ToolRequest
from fenix_mcp.domain.productivity import ProductivityService
from fenix_mcp.infrastructure.context import AppContext


class TodoAction(str, Enum):
    def __new__(cls, value: str, description: str):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    CREATE = ("todo_create", "Cria um novo TODO.")
    LIST = ("todo_list", "Lista TODOs com filtros opcionais.")
    GET = ("todo_get", "Obtém detalhes de um TODO pelo ID.")
    UPDATE = ("todo_update", "Atualiza campos de um TODO existente.")
    DELETE = ("todo_delete", "Remove um TODO pelo ID.")
    STATS = ("todo_stats", "Retorna estatísticas agregadas de TODOs.")
    SEARCH = ("todo_search", "Busca TODOs por termo textual.")
    OVERDUE = ("todo_overdue", "Lista TODOs atrasados.")
    UPCOMING = ("todo_upcoming", "Lista TODOs com vencimento próximo.")
    CATEGORIES = ("todo_categories", "Lista categorias registradas.")
    TAGS = ("todo_tags", "Lista tags registradas.")
    HELP = ("todo_help", "Mostra as ações suportadas e seus usos.")

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
    "Ação de produtividade (TODO). Escolha um dos valores: "
    + ", ".join(
        f"`{member.value}` ({member.description.rstrip('.')})." for member in TodoAction
    )
)


class ProductivityRequest(ToolRequest):
    action: TodoAction = Field(description=ACTION_FIELD_DESCRIPTION)
    id: Optional[str] = Field(default=None, description="Identificador do item TODO.")
    title: Optional[str] = Field(
        default=None, description="Título do TODO (obrigatório em create)."
    )
    content: Optional[str] = Field(
        default=None, description="Conteúdo em Markdown (obrigatório em create)."
    )
    status: Optional[str] = Field(default=None, description="Status do TODO.")
    priority: Optional[str] = Field(default=None, description="Prioridade do TODO.")
    category: Optional[str] = Field(default=None, description="Categoria opcional.")
    tags: Optional[List[str]] = Field(default=None, description="Lista de tags.")
    due_date: Optional[str] = Field(
        default=None, description="Data de vencimento do TODO (ISO)."
    )
    limit: int = Field(
        default=20, ge=1, le=100, description="Limite de resultados em list/search."
    )
    offset: int = Field(default=0, ge=0, description="Offset de paginação.")
    query: Optional[str] = Field(default=None, description="Termo de busca.")
    days: Optional[int] = Field(
        default=None, ge=1, le=30, description="Janela de dias para upcoming."
    )


class ProductivityTool(Tool):
    name = "productivity"
    description = "Operações de produtividade do Fênix Cloud (TODOs)."
    request_model = ProductivityRequest

    def __init__(self, context: AppContext):
        self._context = context
        self._service = ProductivityService(context.api_client, context.logger)

    async def run(self, payload: ProductivityRequest, context: AppContext):
        action = payload.action
        if action is TodoAction.HELP:
            return await self._handle_help()
        if action is TodoAction.CREATE:
            return await self._handle_create(payload)
        if action is TodoAction.LIST:
            return await self._handle_list(payload)
        if action is TodoAction.GET:
            return await self._handle_get(payload)
        if action is TodoAction.UPDATE:
            return await self._handle_update(payload)
        if action is TodoAction.DELETE:
            return await self._handle_delete(payload)
        if action is TodoAction.STATS:
            return await self._handle_stats()
        if action is TodoAction.SEARCH:
            return await self._handle_search(payload)
        if action is TodoAction.OVERDUE:
            return await self._handle_overdue()
        if action is TodoAction.UPCOMING:
            return await self._handle_upcoming(payload)
        if action is TodoAction.CATEGORIES:
            return await self._handle_categories()
        if action is TodoAction.TAGS:
            return await self._handle_tags()
        return text(
            "❌ Ação inválida para productivity.\n\nEscolha um dos valores:\n"
            + "\n".join(f"- `{value}`" for value in TodoAction.choices())
        )

    async def _handle_create(self, payload: ProductivityRequest):
        if not payload.title or not payload.content or not payload.due_date:
            return text("❌ Forneça título, conteúdo e due_date para criar um TODO.")
        todo = await self._service.create_todo(
            title=payload.title,
            content=payload.content,
            status=payload.status or "pending",
            priority=payload.priority or "medium",
            category=payload.category,
            tags=payload.tags or [],
            due_date=payload.due_date,
        )
        return text(self._format_single(todo, header="✅ TODO criado com sucesso!"))

    async def _handle_list(self, payload: ProductivityRequest):
        todos = await self._service.list_todos(
            limit=payload.limit,
            offset=payload.offset,
            status=payload.status,
            priority=payload.priority,
            category=payload.category,
        )
        if not todos:
            return text("📋 Nenhum TODO encontrado.")
        body = "\n\n".join(ProductivityService.format_todo(todo) for todo in todos)
        return text(f"📋 **TODOs ({len(todos)}):**\n\n{body}")

    async def _handle_get(self, payload: ProductivityRequest):
        if not payload.id:
            return text("❌ Informe o ID para consultar um TODO.")
        todo = await self._service.get_todo(payload.id)
        return text(self._format_single(todo, header="📋 TODO encontrado"))

    async def _handle_update(self, payload: ProductivityRequest):
        if not payload.id:
            return text("❌ Informe o ID para atualizar um TODO.")
        fields = {
            "title": payload.title,
            "content": payload.content,
            "status": payload.status,
            "priority": payload.priority,
            "category": payload.category,
            "tags": payload.tags,
            "due_date": payload.due_date,
        }
        todo = await self._service.update_todo(payload.id, **fields)
        return text(self._format_single(todo, header="✅ TODO atualizado"))

    async def _handle_delete(self, payload: ProductivityRequest):
        if not payload.id:
            return text("❌ Informe o ID para excluir um TODO.")
        await self._service.delete_todo(payload.id)
        return text(f"🗑️ TODO {payload.id} removido com sucesso.")

    async def _handle_stats(self):
        stats = await self._service.stats()
        lines = ["📊 **Estatísticas de TODOs**"]
        for key, value in (stats or {}).items():
            lines.append(f"- {key}: {value}")
        return text("\n".join(lines))

    async def _handle_search(self, payload: ProductivityRequest):
        if not payload.query:
            return text("❌ Informe um termo de busca (query).")
        todos = await self._service.search(
            payload.query, limit=payload.limit, offset=payload.offset
        )
        if not todos:
            return text("🔍 Nenhum TODO encontrado para a busca.")
        body = "\n\n".join(ProductivityService.format_todo(todo) for todo in todos)
        return text(f"🔍 **Resultados da busca ({len(todos)}):**\n\n{body}")

    async def _handle_overdue(self):
        todos = await self._service.overdue()
        if not todos:
            return text("✅ Sem TODOs atrasados no momento.")
        body = "\n\n".join(ProductivityService.format_todo(todo) for todo in todos)
        return text(f"⏰ **TODOs atrasados ({len(todos)}):**\n\n{body}")

    async def _handle_upcoming(self, payload: ProductivityRequest):
        todos = await self._service.upcoming(days=payload.days)
        if not todos:
            return text("📅 Nenhum TODO previsto para o período informado.")
        body = "\n\n".join(ProductivityService.format_todo(todo) for todo in todos)
        header = f"📅 TODOs programados ({len(todos)}):"
        if payload.days:
            header += f" próximos {payload.days} dias"
        return text(f"{header}\n\n{body}")

    async def _handle_categories(self):
        categories = await self._service.categories()
        if not categories:
            return text("🏷️ Nenhuma categoria registrada ainda.")
        body = "\n".join(f"- {category}" for category in categories)
        return text(f"🏷️ **Categorias utilizadas:**\n{body}")

    async def _handle_tags(self):
        tags = await self._service.tags()
        if not tags:
            return text("🔖 Nenhuma tag registrada ainda.")
        body = "\n".join(f"- {tag}" for tag in tags)
        return text(f"🔖 **Tags utilizadas:**\n{body}")

    async def _handle_help(self):
        return text(
            "📚 **Ações disponíveis para productivity**\n\n"
            + TodoAction.formatted_help()
        )

    @staticmethod
    def _format_single(todo: Dict[str, Any], *, header: str) -> str:
        return "\n".join([header, "", ProductivityService.format_todo(todo)])
