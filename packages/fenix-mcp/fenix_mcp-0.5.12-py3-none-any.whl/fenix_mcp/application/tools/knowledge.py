# SPDX-License-Identifier: MIT
"""Knowledge tool implementation updated for the expanded Fênix API."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from fenix_mcp.application.presenters import text
from fenix_mcp.application.tool_base import Tool, ToolRequest
from fenix_mcp.domain.knowledge import KnowledgeService, _format_date
from fenix_mcp.infrastructure.context import AppContext


class KnowledgeAction(str, Enum):
    def __new__(cls, value: str, description: str):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    # Work items
    WORK_CREATE = (
        "work_create",
        "Cria um work item com título, status e vínculos opcionais.",
    )
    WORK_LIST = (
        "work_list",
        "Lista work items com filtros de status, prioridade e contexto.",
    )
    WORK_GET = ("work_get", "Obtém detalhes completos de um work item pelo ID.")
    WORK_UPDATE = (
        "work_update",
        "Atualiza campos específicos de um work item existente.",
    )
    WORK_DELETE = ("work_delete", "Remove um work item definitivamente.")
    WORK_BACKLOG = ("work_backlog", "Lista itens do backlog de um time.")
    WORK_SEARCH = ("work_search", "Busca work items por texto com filtros adicionais.")
    WORK_ANALYTICS = ("work_analytics", "Retorna métricas consolidadas de work items.")
    WORK_BY_BOARD = ("work_by_board", "Lista work items associados a um board.")
    WORK_BY_SPRINT = ("work_by_sprint", "Lista work items associados a um sprint.")

    # Boards
    BOARD_LIST = ("board_list", "Lista boards disponíveis com filtros opcionais.")
    BOARD_BY_TEAM = ("board_by_team", "Lista boards de um time específico.")
    BOARD_FAVORITES = ("board_favorites", "Lista boards marcados como favoritos.")
    BOARD_GET = ("board_get", "Obtém detalhes de um board pelo ID.")
    BOARD_COLUMNS = ("board_columns", "Lista colunas configuradas para um board.")

    # Sprints
    SPRINT_LIST = ("sprint_list", "Lista sprints disponíveis com filtros opcionais.")
    SPRINT_BY_TEAM = ("sprint_by_team", "Lista sprints associados a um time.")
    SPRINT_ACTIVE = ("sprint_active", "Obtém o sprint ativo de um time.")
    SPRINT_GET = ("sprint_get", "Obtém detalhes de um sprint pelo ID.")
    SPRINT_WORK_ITEMS = (
        "sprint_work_items",
        "Lista work items vinculados a um sprint.",
    )

    # Modes
    MODE_CREATE = ("mode_create", "Cria um modo com conteúdo e metadados opcionais.")
    MODE_LIST = ("mode_list", "Lista modes cadastrados.")
    MODE_GET = ("mode_get", "Obtém detalhes completos de um modo.")
    MODE_UPDATE = ("mode_update", "Atualiza propriedades de um modo existente.")
    MODE_DELETE = ("mode_delete", "Remove um modo.")
    MODE_RULE_ADD = ("mode_rule_add", "Associa uma regra a um modo.")
    MODE_RULE_REMOVE = (
        "mode_rule_remove",
        "Remove a associação de uma regra com um modo.",
    )
    MODE_RULES = ("mode_rules", "Lista regras associadas a um modo.")

    # Rules
    RULE_CREATE = ("rule_create", "Cria uma regra com conteúdo e metadados.")
    RULE_LIST = ("rule_list", "Lista regras cadastradas.")
    RULE_GET = ("rule_get", "Obtém detalhes de uma regra.")
    RULE_UPDATE = ("rule_update", "Atualiza uma regra existente.")
    RULE_DELETE = ("rule_delete", "Remove uma regra.")

    # Documentation
    DOC_CREATE = ("doc_create", "Cria um item de documentação.")
    DOC_LIST = ("doc_list", "Lista itens de documentação com filtros.")
    DOC_GET = ("doc_get", "Obtém detalhes de um item de documentação.")
    DOC_UPDATE = ("doc_update", "Atualiza um item de documentação.")
    DOC_DELETE = ("doc_delete", "Remove um item de documentação.")
    DOC_SEARCH = ("doc_search", "Busca itens de documentação por texto.")
    DOC_ROOTS = ("doc_roots", "Lista documentos raiz disponíveis.")
    DOC_RECENT = ("doc_recent", "Lista documentos acessados recentemente.")
    DOC_ANALYTICS = ("doc_analytics", "Retorna analytics dos documentos.")
    DOC_CHILDREN = ("doc_children", "Lista documentos filhos de um item.")
    DOC_TREE = ("doc_tree", "Recupera a árvore direta de um documento.")
    DOC_FULL_TREE = ("doc_full_tree", "Recupera a árvore completa de documentação.")
    DOC_MOVE = ("doc_move", "Move um documento para outro pai.")
    DOC_PUBLISH = ("doc_publish", "Altera status de publicação de um documento.")
    DOC_VERSION = ("doc_version", "Gera ou recupera versão de um documento.")
    DOC_DUPLICATE = ("doc_duplicate", "Duplica um documento existente.")

    HELP = ("knowledge_help", "Mostra as ações disponíveis e seus usos.")

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


ACTION_FIELD_DESCRIPTION = "Ação de conhecimento. Escolha um dos valores: " + ", ".join(
    f"`{member.value}` ({member.description.rstrip('.')})."
    for member in KnowledgeAction
)


_ALLOWED_DOC_TYPES = {
    "folder",
    "page",
    "api_doc",
    "guide",
}


class KnowledgeRequest(ToolRequest):
    action: KnowledgeAction = Field(description=ACTION_FIELD_DESCRIPTION)
    id: Optional[str] = Field(default=None, description="ID principal do recurso.")
    limit: int = Field(default=20, ge=1, le=100, description="Limite de resultados.")
    offset: int = Field(
        default=0, ge=0, description="Offset de paginação (quando suportado)."
    )
    team_id: Optional[str] = Field(
        default=None, description="ID do time para filtros (boards/sprints/docs)."
    )
    board_id: Optional[str] = Field(default=None, description="ID do board associado.")
    sprint_id: Optional[str] = Field(
        default=None, description="ID do sprint associado."
    )
    epic_id: Optional[str] = Field(default=None, description="ID do épico associado.")
    query: Optional[str] = Field(default=None, description="Filtro/busca.")
    return_content: Optional[bool] = Field(
        default=None, description="Retorna conteúdo completo."
    )
    return_description: Optional[bool] = Field(
        default=None, description="Retorna descrição completa."
    )
    return_metadata: Optional[bool] = Field(
        default=None, description="Retorna metadados completos."
    )

    # Work item fields
    work_title: Optional[str] = Field(default=None, description="Título do work item.")
    work_description: Optional[str] = Field(
        default=None, description="Descrição do work item."
    )
    work_type: Optional[str] = Field(default="task", description="Tipo do work item.")
    work_priority: Optional[str] = Field(
        default=None, description="Prioridade do work item."
    )
    story_points: Optional[int] = Field(default=None, description="Story points.")
    assignee_id: Optional[str] = Field(default=None, description="ID do responsável.")
    parent_id: Optional[str] = Field(default=None, description="ID do item pai.")

    # Mode fields
    mode_id: Optional[str] = Field(default=None, description="ID do modo relacionado.")
    mode_name: Optional[str] = Field(default=None, description="Nome do modo.")
    mode_description: Optional[str] = Field(
        default=None, description="Descrição do modo."
    )
    mode_content: Optional[str] = Field(default=None, description="Conteúdo do modo.")
    mode_is_default: Optional[bool] = Field(
        default=None, description="Indica se o modo é padrão."
    )

    # Rule fields
    rule_id: Optional[str] = Field(default=None, description="ID da regra relacionada.")
    rule_name: Optional[str] = Field(default=None, description="Nome da regra.")
    rule_description: Optional[str] = Field(
        default=None, description="Descrição da regra."
    )
    rule_content: Optional[str] = Field(default=None, description="Conteúdo da regra.")
    rule_is_default: Optional[bool] = Field(default=None, description="Regra padrão.")

    # Documentation fields
    doc_title: Optional[str] = Field(
        default=None, description="Título da documentação."
    )
    doc_description: Optional[str] = Field(default=None, description="Descrição.")
    doc_content: Optional[str] = Field(
        default=None, description="Conteúdo da documentação."
    )
    doc_status: Optional[str] = Field(
        default=None, description="Status da documentação."
    )
    doc_type: Optional[str] = Field(default=None, description="Tipo da documentação.")
    doc_language: Optional[str] = Field(
        default=None, description="Idioma da documentação."
    )
    doc_parent_id: Optional[str] = Field(default=None, description="Documento pai.")
    doc_team_id: Optional[str] = Field(
        default=None, description="Time responsável pela documentação."
    )
    doc_owner_id: Optional[str] = Field(default=None, description="ID do dono.")
    doc_reviewer_id: Optional[str] = Field(default=None, description="ID do revisor.")
    doc_version: Optional[str] = Field(default=None, description="Versão.")
    doc_category: Optional[str] = Field(default=None, description="Categoria.")
    doc_tags: Optional[List[str]] = Field(default=None, description="Tags.")
    doc_position: Optional[int] = Field(
        default=None, description="Posição desejada ao mover documentos."
    )
    doc_emoji: Optional[str] = Field(
        default=None, description="Emoji exibido junto ao documento."
    )
    doc_emote: Optional[str] = Field(
        default=None, description="Alias para emoji, mantido por compatibilidade."
    )


class KnowledgeTool(Tool):
    name = "knowledge"
    description = "Operações de conhecimento do Fênix Cloud (Work Items, Boards, Sprints, Modes, Rules, Docs)."
    request_model = KnowledgeRequest

    def __init__(self, context: AppContext):
        self._context = context
        self._service = KnowledgeService(context.api_client, context.logger)

    async def run(self, payload: KnowledgeRequest, context: AppContext):
        action = payload.action
        if action is KnowledgeAction.HELP:
            return await self._handle_help()
        if action.value.startswith("work_"):
            return await self._run_work(payload)
        if action.value.startswith("board_"):
            return await self._run_board(payload)
        if action.value.startswith("sprint_"):
            return await self._run_sprint(payload)
        if action.value.startswith("mode_"):
            return await self._run_mode(payload)
        if action.value.startswith("rule_"):
            return await self._run_rule(payload)
        if action.value.startswith("doc_"):
            return await self._run_doc(payload)
        return text(
            "❌ Ação inválida para knowledge.\n\nEscolha um dos valores:\n"
            + "\n".join(f"- `{value}`" for value in KnowledgeAction.choices())
        )

    # ------------------------------------------------------------------
    # Work items
    # ------------------------------------------------------------------
    async def _run_work(self, payload: KnowledgeRequest):
        action = payload.action
        if action is KnowledgeAction.WORK_CREATE:
            if not payload.work_title:
                return text("❌ Informe work_title para criar o item.")
            work = await self._service.work_create(
                {
                    "title": payload.work_title,
                    "description": payload.work_description,
                    "item_type": payload.work_type,
                    "priority": payload.work_priority,
                    "story_points": payload.story_points,
                    "assignee_id": payload.assignee_id,
                    "sprint_id": payload.sprint_id,
                    "board_id": payload.board_id,
                    "parent_id": payload.parent_id,
                }
            )
            return text(_format_work(work, header="✅ Work item criado"))

        if action is KnowledgeAction.WORK_LIST:
            items = await self._service.work_list(
                limit=payload.limit,
                offset=payload.offset,
                priority=payload.work_priority,
                type=payload.work_type,
                assignee=payload.assignee_id,
                sprint=payload.sprint_id,
                board=payload.board_id,
            )
            if not items:
                return text("🎯 Nenhum work item encontrado.")
            body = "\n\n".join(_format_work(item) for item in items)
            return text(f"🎯 **Work items ({len(items)}):**\n\n{body}")

        if action is KnowledgeAction.WORK_GET:
            if not payload.id:
                return text("❌ Informe o ID do work item.")
            work = await self._service.work_get(payload.id)
            return text(_format_work(work, header="🎯 Detalhes do work item"))

        if action is KnowledgeAction.WORK_UPDATE:
            if not payload.id:
                return text("❌ Informe o ID do work item.")
            work = await self._service.work_update(
                payload.id,
                {
                    "title": payload.work_title,
                    "description": payload.work_description,
                    "item_type": payload.work_type,
                    "priority": payload.work_priority,
                    "story_points": payload.story_points,
                    "assignee_id": payload.assignee_id,
                    "sprint_id": payload.sprint_id,
                    "board_id": payload.board_id,
                    "parent_id": payload.parent_id,
                },
            )
            return text(_format_work(work, header="✅ Work item atualizado"))

        if action is KnowledgeAction.WORK_DELETE:
            if not payload.id:
                return text("❌ Informe o ID do work item.")
            await self._service.work_delete(payload.id)
            return text(f"🗑️ Work item {payload.id} removido.")

        if action is KnowledgeAction.WORK_BACKLOG:
            if not payload.team_id:
                return text("❌ Informe team_id para consultar o backlog.")
            items = await self._service.work_backlog(team_id=payload.team_id)
            if not items:
                return text("📋 Backlog vazio para o time informado.")
            body = "\n\n".join(_format_work(item) for item in items)
            return text(f"📋 **Backlog ({len(items)}):**\n\n{body}")

        if action is KnowledgeAction.WORK_SEARCH:
            if not payload.query or not payload.team_id:
                return text("❌ Informe query e team_id para buscar work items.")
            items = await self._service.work_search(
                query=payload.query,
                team_id=payload.team_id,
                limit=payload.limit,
            )
            if not items:
                return text("🔍 Nenhum work item encontrado.")
            body = "\n\n".join(_format_work(item) for item in items)
            return text(f"🔍 **Resultados ({len(items)}):**\n\n{body}")

        if action is KnowledgeAction.WORK_ANALYTICS:
            if not payload.team_id:
                return text("❌ Informe team_id para obter analytics.")
            analytics = await self._service.work_analytics(team_id=payload.team_id)
            lines = ["📊 **Analytics de Work Items**"]
            for key, value in analytics.items():
                lines.append(f"- {key}: {value}")
            return text("\n".join(lines))

        if action is KnowledgeAction.WORK_BY_BOARD:
            if not payload.board_id:
                return text("❌ Informe board_id para listar os itens.")
            items = await self._service.work_by_board(board_id=payload.board_id)
            if not items:
                return text("🗂️ Nenhum work item para o board informado.")
            body = "\n\n".join(_format_work(item) for item in items)
            return text(f"🗂️ **Itens do board ({len(items)}):**\n\n{body}")

        if action is KnowledgeAction.WORK_BY_SPRINT:
            if not payload.sprint_id:
                return text("❌ Informe sprint_id para listar os itens.")
            items = await self._service.work_by_sprint(sprint_id=payload.sprint_id)
            if not items:
                return text("🏃 Nenhum item vinculado ao sprint informado.")
            body = "\n\n".join(_format_work(item) for item in items)
            return text(f"🏃 **Work items do sprint ({len(items)}):**\n\n{body}")

        return text(
            "❌ Ação de work item não suportada.\n\nEscolha um dos valores:\n"
            + "\n".join(
                f"- `{value}`"
                for value in KnowledgeAction.choices()
                if value.startswith("work_")
            )
        )

    # ------------------------------------------------------------------
    # Boards
    # ------------------------------------------------------------------
    async def _run_board(self, payload: KnowledgeRequest):
        action = payload.action
        if action is KnowledgeAction.BOARD_LIST:
            boards = await self._service.board_list(
                limit=payload.limit, offset=payload.offset
            )
            if not boards:
                return text("🗂️ Nenhum board encontrado.")
            body = "\n\n".join(_format_board(board) for board in boards)
            return text(f"🗂️ **Boards ({len(boards)}):**\n\n{body}")

        if action is KnowledgeAction.BOARD_BY_TEAM:
            if not payload.team_id:
                return text("❌ Informe team_id para listar boards do time.")
            boards = await self._service.board_list_by_team(payload.team_id)
            if not boards:
                return text("🗂️ Nenhum board cadastrado para o time.")
            body = "\n\n".join(_format_board(board) for board in boards)
            return text(f"🗂️ **Boards do time ({len(boards)}):**\n\n{body}")

        if action is KnowledgeAction.BOARD_FAVORITES:
            boards = await self._service.board_favorites()
            if not boards:
                return text("⭐ Nenhum board favorito cadastrado.")
            body = "\n\n".join(_format_board(board) for board in boards)
            return text(f"⭐ **Boards favoritos ({len(boards)}):**\n\n{body}")

        if action is KnowledgeAction.BOARD_GET:
            if not payload.board_id:
                return text("❌ Informe board_id para consultar detalhes.")
            board = await self._service.board_get(payload.board_id)
            return text(_format_board(board, header="🗂️ Detalhes do board"))

        if action is KnowledgeAction.BOARD_COLUMNS:
            if not payload.board_id:
                return text("❌ Informe board_id para listar colunas.")
            columns = await self._service.board_columns(payload.board_id)
            if not columns:
                return text("📊 Board sem colunas cadastradas.")
            body = "\n".join(
                f"- {col.get('name', 'Sem nome')} (ID: {col.get('id')})"
                for col in columns
            )
            return text(f"📊 **Colunas do board:**\n{body}")

        return text(
            "❌ Ação de board não suportada.\n\nEscolha um dos valores:\n"
            + "\n".join(
                f"- `{value}`"
                for value in KnowledgeAction.choices()
                if value.startswith("board_")
            )
        )

    # ------------------------------------------------------------------
    # Sprints
    # ------------------------------------------------------------------
    async def _run_sprint(self, payload: KnowledgeRequest):
        action = payload.action
        if action is KnowledgeAction.SPRINT_LIST:
            sprints = await self._service.sprint_list(
                limit=payload.limit, offset=payload.offset
            )
            if not sprints:
                return text("🏃 Nenhum sprint encontrado.")
            body = "\n\n".join(_format_sprint(sprint) for sprint in sprints)
            return text(f"🏃 **Sprints ({len(sprints)}):**\n\n{body}")

        if action is KnowledgeAction.SPRINT_BY_TEAM:
            if not payload.team_id:
                return text("❌ Informe team_id para listar sprints do time.")
            sprints = await self._service.sprint_list_by_team(payload.team_id)
            if not sprints:
                return text("🏃 Nenhum sprint cadastrado para o time.")
            body = "\n\n".join(_format_sprint(sprint) for sprint in sprints)
            return text(f"🏃 **Sprints do time ({len(sprints)}):**\n\n{body}")

        if action is KnowledgeAction.SPRINT_ACTIVE:
            if not payload.team_id:
                return text("❌ Informe team_id para consultar o sprint ativo.")
            sprint = await self._service.sprint_active(payload.team_id)
            if not sprint:
                return text("⏳ Nenhum sprint ativo no momento.")
            return text(_format_sprint(sprint, header="⏳ Sprint ativo"))

        if action is KnowledgeAction.SPRINT_GET:
            if not payload.sprint_id:
                return text("❌ Informe sprint_id para consultar detalhes.")
            sprint = await self._service.sprint_get(payload.sprint_id)
            return text(_format_sprint(sprint, header="🏃 Detalhes do sprint"))

        if action is KnowledgeAction.SPRINT_WORK_ITEMS:
            if not payload.sprint_id:
                return text("❌ Informe sprint_id para listar os itens.")
            items = await self._service.sprint_work_items(payload.sprint_id)
            if not items:
                return text("🏃 Nenhum item vinculado ao sprint informado.")
            body = "\n\n".join(_format_work(item) for item in items)
            return text(f"🏃 **Itens do sprint ({len(items)}):**\n\n{body}")

        return text(
            "❌ Ação de sprint não suportada.\n\nEscolha um dos valores:\n"
            + "\n".join(
                f"- `{value}`"
                for value in KnowledgeAction.choices()
                if value.startswith("sprint_")
            )
        )

    # ------------------------------------------------------------------
    # Modes
    # ------------------------------------------------------------------
    async def _run_mode(self, payload: KnowledgeRequest):
        action = payload.action
        if action is KnowledgeAction.MODE_CREATE:
            if not payload.mode_name:
                return text("❌ Informe mode_name para criar o modo.")
            mode = await self._service.mode_create(
                {
                    "name": payload.mode_name,
                    "description": payload.mode_description,
                    "content": payload.mode_content,
                    "is_default": payload.mode_is_default,
                }
            )
            return text(_format_mode(mode, header="✅ Modo criado"))

        if action is KnowledgeAction.MODE_LIST:
            modes = await self._service.mode_list(
                include_rules=payload.return_metadata,
                return_description=payload.return_description,
                return_metadata=payload.return_metadata,
            )
            if not modes:
                return text("🎭 Nenhum modo encontrado.")
            body = "\n\n".join(_format_mode(mode) for mode in modes)
            return text(f"🎭 **Modes ({len(modes)}):**\n\n{body}")

        if action is KnowledgeAction.MODE_GET:
            if not payload.mode_id:
                return text("❌ Informe mode_id para consultar detalhes.")
            mode = await self._service.mode_get(
                payload.mode_id,
                return_description=payload.return_description,
                return_metadata=payload.return_metadata,
            )
            return text(_format_mode(mode, header="🎭 Detalhes do modo"))

        if action is KnowledgeAction.MODE_UPDATE:
            if not payload.mode_id:
                return text("❌ Informe mode_id para atualizar.")
            mode = await self._service.mode_update(
                payload.mode_id,
                {
                    "name": payload.mode_name,
                    "description": payload.mode_description,
                    "content": payload.mode_content,
                    "is_default": payload.mode_is_default,
                },
            )
            return text(_format_mode(mode, header="✅ Modo atualizado"))

        if action is KnowledgeAction.MODE_DELETE:
            if not payload.mode_id:
                return text("❌ Informe mode_id para remover.")
            await self._service.mode_delete(payload.mode_id)
            return text(f"🗑️ Modo {payload.mode_id} removido.")

        if action is KnowledgeAction.MODE_RULE_ADD:
            if not payload.mode_id or not payload.rule_id:
                return text("❌ Informe mode_id e rule_id para associar.")
            link = await self._service.mode_rule_add(payload.mode_id, payload.rule_id)
            return text(
                "\n".join(
                    [
                        "🔗 **Regra associada ao modo!**",
                        f"Modo: {link.get('modeId', payload.mode_id)}",
                        f"Regra: {link.get('ruleId', payload.rule_id)}",
                    ]
                )
            )

        if action is KnowledgeAction.MODE_RULE_REMOVE:
            if not payload.mode_id or not payload.rule_id:
                return text("❌ Informe mode_id e rule_id para remover a associação.")
            await self._service.mode_rule_remove(payload.mode_id, payload.rule_id)
            return text("🔗 Associação removida.")

        if action is KnowledgeAction.MODE_RULES:
            if payload.mode_id:
                rules = await self._service.mode_rules(payload.mode_id)
                context_label = f"modo {payload.mode_id}"
            elif payload.rule_id:
                rules = await self._service.mode_rules_for_rule(payload.rule_id)
                context_label = f"regra {payload.rule_id}"
            else:
                return text("❌ Informe mode_id ou rule_id para listar associações.")
            if not rules:
                return text("🔗 Nenhuma associação encontrada.")
            body = "\n".join(
                f"- {item.get('name', 'Sem nome')} (ID: {item.get('id')})"
                for item in rules
            )
            return text(f"🔗 **Associações para {context_label}:**\n{body}")

        return text(
            "❌ Ação de modo não suportada.\n\nEscolha um dos valores:\n"
            + "\n".join(
                f"- `{value}`"
                for value in KnowledgeAction.choices()
                if value.startswith("mode_")
            )
        )

    # ------------------------------------------------------------------
    # Rules
    # ------------------------------------------------------------------
    async def _run_rule(self, payload: KnowledgeRequest):
        action = payload.action
        if action is KnowledgeAction.RULE_CREATE:
            if not payload.rule_name or not payload.rule_content:
                return text("❌ Informe rule_name e rule_content.")
            rule = await self._service.rule_create(
                {
                    "name": payload.rule_name,
                    "description": payload.rule_description,
                    "content": payload.rule_content,
                    "is_default": payload.rule_is_default,
                }
            )
            return text(_format_rule(rule, header="✅ Regra criada"))

        if action is KnowledgeAction.RULE_LIST:
            rules = await self._service.rule_list(
                return_description=payload.return_description,
                return_metadata=payload.return_metadata,
                return_modes=payload.return_metadata,
            )
            if not rules:
                return text("📋 Nenhuma regra encontrada.")
            body = "\n\n".join(_format_rule(rule) for rule in rules)
            return text(f"📋 **Regras ({len(rules)}):**\n\n{body}")

        if action is KnowledgeAction.RULE_GET:
            if not payload.rule_id:
                return text("❌ Informe rule_id para consultar detalhes.")
            rule = await self._service.rule_get(
                payload.rule_id,
                return_description=payload.return_description,
                return_metadata=payload.return_metadata,
                return_modes=payload.return_metadata,
            )
            return text(_format_rule(rule, header="📋 Detalhes da regra"))

        if action is KnowledgeAction.RULE_UPDATE:
            if not payload.rule_id:
                return text("❌ Informe rule_id para atualizar.")
            rule = await self._service.rule_update(
                payload.rule_id,
                {
                    "name": payload.rule_name,
                    "description": payload.rule_description,
                    "content": payload.rule_content,
                    "is_default": payload.rule_is_default,
                },
            )
            return text(_format_rule(rule, header="✅ Regra atualizada"))

        if action is KnowledgeAction.RULE_DELETE:
            if not payload.rule_id:
                return text("❌ Informe rule_id para remover.")
            await self._service.rule_delete(payload.rule_id)
            return text(f"🗑️ Regra {payload.rule_id} removida.")

        return text(
            "❌ Ação de regra não suportada.\n\nEscolha um dos valores:\n"
            + "\n".join(
                f"- `{value}`"
                for value in KnowledgeAction.choices()
                if value.startswith("rule_")
            )
        )

    # ------------------------------------------------------------------
    # Documentation
    # ------------------------------------------------------------------
    async def _run_doc(self, payload: KnowledgeRequest):
        action = payload.action
        if action is KnowledgeAction.DOC_CREATE:
            if not payload.doc_title:
                return text("❌ Informe doc_title para criar a documentação.")
            if payload.doc_type and payload.doc_type not in _ALLOWED_DOC_TYPES:
                allowed = ", ".join(sorted(_ALLOWED_DOC_TYPES))
                return text(
                    "❌ doc_type inválido. Use um dos valores suportados: " + allowed
                )
            doc = await self._service.doc_create(
                {
                    "title": payload.doc_title,
                    "description": payload.doc_description,
                    "content": payload.doc_content,
                    "status": payload.doc_status,
                    "doc_type": payload.doc_type,
                    "language": payload.doc_language,
                    "parent_id": payload.doc_parent_id,
                    "team_id": payload.doc_team_id or payload.team_id,
                    "owner_id": payload.doc_owner_id,
                    "reviewer_id": payload.doc_reviewer_id,
                    "version": payload.doc_version,
                    "category": payload.doc_category,
                    "tags": payload.doc_tags,
                    "emoji": payload.doc_emoji or payload.doc_emote,
                }
            )
            return text(_format_doc(doc, header="✅ Documentação criada"))

        if action is KnowledgeAction.DOC_LIST:
            docs = await self._service.doc_list(
                limit=payload.limit,
                offset=payload.offset,
                returnContent=payload.return_content,
            )
            if not docs:
                return text("📄 Nenhuma documentação encontrada.")
            body = "\n\n".join(_format_doc(doc) for doc in docs)
            return text(f"📄 **Documentos ({len(docs)}):**\n\n{body}")

        if action is KnowledgeAction.DOC_GET:
            if not payload.id:
                return text("❌ Informe o ID da documentação.")
            doc = await self._service.doc_get(
                payload.id,
                returnContent=payload.return_content,
            )
            return text(_format_doc(doc, header="📄 Detalhes da documentação"))

        if action is KnowledgeAction.DOC_UPDATE:
            if not payload.id:
                return text("❌ Informe o ID da documentação.")
            if payload.doc_type and payload.doc_type not in _ALLOWED_DOC_TYPES:
                allowed = ", ".join(sorted(_ALLOWED_DOC_TYPES))
                return text(
                    "❌ doc_type inválido. Use um dos valores suportados: " + allowed
                )
            doc = await self._service.doc_update(
                payload.id,
                {
                    "title": payload.doc_title,
                    "description": payload.doc_description,
                    "content": payload.doc_content,
                    "status": payload.doc_status,
                    "doc_type": payload.doc_type,
                    "language": payload.doc_language,
                    "parent_id": payload.doc_parent_id,
                    "team_id": payload.doc_team_id or payload.team_id,
                    "owner_id": payload.doc_owner_id,
                    "reviewer_id": payload.doc_reviewer_id,
                    "version": payload.doc_version,
                    "category": payload.doc_category,
                    "tags": payload.doc_tags,
                    "emoji": payload.doc_emoji or payload.doc_emote,
                },
            )
            return text(_format_doc(doc, header="✅ Documentação atualizada"))

        if action is KnowledgeAction.DOC_DELETE:
            if not payload.id:
                return text("❌ Informe o ID da documentação.")
            await self._service.doc_delete(payload.id)
            return text(f"🗑️ Documentação {payload.id} removida.")

        if action is KnowledgeAction.DOC_SEARCH:
            if not payload.query or not (payload.doc_team_id or payload.team_id):
                return text("❌ Informe query e team_id para buscar documentação.")
            docs = await self._service.doc_search(
                query=payload.query,
                team_id=payload.doc_team_id or payload.team_id,
                limit=payload.limit,
            )
            if not docs:
                return text(
                    "🔍 Nenhum documento encontrado para os filtros informados."
                )
            body = "\n\n".join(_format_doc(doc) for doc in docs)
            return text(f"🔍 **Resultados ({len(docs)}):**\n\n{body}")

        if action is KnowledgeAction.DOC_ROOTS:
            if not (payload.doc_team_id or payload.team_id):
                return text("❌ Informe team_id para listar raízes.")
            docs = await self._service.doc_roots(
                team_id=payload.doc_team_id or payload.team_id
            )
            if not docs:
                return text("📚 Nenhuma raiz encontrada.")
            body = "\n".join(
                f"- {doc.get('title', 'Sem título')} (ID: {doc.get('id')})"
                for doc in docs
            )
            return text(f"📚 **Raízes de documentação:**\n{body}")

        if action is KnowledgeAction.DOC_RECENT:
            if not (payload.doc_team_id or payload.team_id):
                return text("❌ Informe team_id para listar documentos recentes.")
            docs = await self._service.doc_recent(
                team_id=payload.doc_team_id or payload.team_id,
                limit=payload.limit,
            )
            if not docs:
                return text("🕒 Nenhuma documentação recente encontrada.")
            body = "\n\n".join(_format_doc(doc) for doc in docs)
            return text(f"🕒 **Documentos recentes ({len(docs)}):**\n\n{body}")

        if action is KnowledgeAction.DOC_ANALYTICS:
            if not (payload.doc_team_id or payload.team_id):
                return text("❌ Informe team_id para obter analytics.")
            analytics = await self._service.doc_analytics(
                team_id=payload.doc_team_id or payload.team_id
            )
            lines = ["📊 **Analytics de Documentação**"]
            for key, value in analytics.items():
                lines.append(f"- {key}: {value}")
            return text("\n".join(lines))

        if action is KnowledgeAction.DOC_CHILDREN:
            if not payload.id:
                return text("❌ Informe o ID da documentação.")
            docs = await self._service.doc_children(payload.id)
            if not docs:
                return text("📄 Nenhum filho cadastrado para o documento informado.")
            body = "\n".join(
                f"- {doc.get('title', 'Sem título')} (ID: {doc.get('id')})"
                for doc in docs
            )
            return text(f"📄 **Filhos:**\n{body}")

        if action is KnowledgeAction.DOC_TREE:
            if not payload.id:
                return text("❌ Informe o ID da documentação.")
            tree = await self._service.doc_tree(payload.id)
            return text(f"🌳 **Árvore de documentação para {payload.id}:**\n{tree}")

        if action is KnowledgeAction.DOC_FULL_TREE:
            tree = await self._service.doc_full_tree()
            return text(f"🌳 **Árvore completa de documentação:**\n{tree}")

        if action is KnowledgeAction.DOC_MOVE:
            if not payload.id:
                return text("❌ Informe o ID da documentação.")
            if payload.doc_parent_id is None and payload.doc_position is None:
                return text(
                    "❌ Informe doc_parent_id, doc_position ou ambos para mover."
                )
            move_payload = {
                "new_parent_id": payload.doc_parent_id,
                "new_position": payload.doc_position,
            }
            doc = await self._service.doc_move(payload.id, move_payload)
            return text(_format_doc(doc, header="📦 Documentação movida"))

        if action is KnowledgeAction.DOC_PUBLISH:
            if not payload.id:
                return text("❌ Informe o ID da documentação.")
            result = await self._service.doc_publish(payload.id)
            return text(f"🗞️ Documento publicado: {result}")

        if action is KnowledgeAction.DOC_VERSION:
            if not payload.id:
                return text("❌ Informe o ID da documentação.")
            if not payload.doc_version:
                return text(
                    "❌ Informe doc_version com o número/identificador da versão."
                )
            version_payload = {
                "title": payload.doc_title or f"Version {payload.doc_version}",
                "version": payload.doc_version,
                "content": payload.doc_content,
            }
            doc = await self._service.doc_version(payload.id, version_payload)
            return text(_format_doc(doc, header="🗞️ Nova versão criada"))

        if action is KnowledgeAction.DOC_DUPLICATE:
            if not payload.id:
                return text("❌ Informe o ID da documentação.")
            if not payload.doc_title:
                return text("❌ Informe doc_title para nomear a cópia.")
            doc = await self._service.doc_duplicate(
                payload.id,
                {
                    "title": payload.doc_title,
                    "team_id": payload.doc_team_id or payload.team_id,
                },
            )
            return text(_format_doc(doc, header="🗂️ Documento duplicado"))

        return text(
            "❌ Ação de documentação não suportada.\n\nEscolha um dos valores:\n"
            + "\n".join(
                f"- `{value}`"
                for value in KnowledgeAction.choices()
                if value.startswith("doc_")
            )
        )

    async def _handle_help(self):
        return text(
            "📚 **Ações disponíveis para knowledge**\n\n"
            + KnowledgeAction.formatted_help()
        )


def _format_work(item: Dict[str, Any], *, header: Optional[str] = None) -> str:
    lines: List[str] = []
    if header:
        lines.append(header)
        lines.append("")

    # Extract title
    title = item.get("title") or item.get("name") or "Sem título"

    # Extract status
    status = item.get("status") or item.get("state") or "desconhecido"

    # Extract priority
    priority = item.get("priority") or item.get("priority_level") or "indefinido"

    # Extract ID
    item_id = item.get("id", "N/A")

    # Extract assignee - check both assignee_id and assignee object
    assignee = item.get("assignee_id")
    if not assignee and item.get("assignee"):
        assignee = item.get("assignee", {}).get("name") or item.get("assignee", {}).get(
            "id"
        )
    if not assignee:
        assignee = "N/A"

    lines.extend(
        [
            f"🎯 **{title}**",
            f"ID: {item_id}",
            f"Status: {status}",
            f"Prioridade: {priority}",
            f"Responsável: {assignee}",
        ]
    )
    if item.get("due_date") or item.get("dueDate"):
        lines.append(
            f"Vencimento: {_format_date(item.get('due_date') or item.get('dueDate'))}"
        )
    return "\n".join(lines)


def _format_board(board: Dict[str, Any], header: Optional[str] = None) -> str:
    lines: List[str] = []
    if header:
        lines.append(header)
        lines.append("")
    lines.extend(
        [
            f"🗂️ **{board.get('name', 'Sem nome')}**",
            f"ID: {board.get('id', 'N/A')}",
            f"Time: {board.get('team_id', 'N/A')}",
            f"Colunas: {len(board.get('columns', []))}",
        ]
    )
    return "\n".join(lines)


def _format_sprint(sprint: Dict[str, Any], header: Optional[str] = None) -> str:
    lines: List[str] = []
    if header:
        lines.append(header)
        lines.append("")
    lines.extend(
        [
            f"🏃 **{sprint.get('name', 'Sem nome')}**",
            f"ID: {sprint.get('id', 'N/A')}",
            f"Status: {sprint.get('status', 'N/A')}",
            f"Time: {sprint.get('team_id', 'N/A')}",
        ]
    )
    if sprint.get("start_date") or sprint.get("startDate"):
        lines.append(
            f"Início: {_format_date(sprint.get('start_date') or sprint.get('startDate'))}"
        )
    if sprint.get("end_date") or sprint.get("endDate"):
        lines.append(
            f"Fim: {_format_date(sprint.get('end_date') or sprint.get('endDate'))}"
        )
    return "\n".join(lines)


def _format_mode(mode: Dict[str, Any], header: Optional[str] = None) -> str:
    lines: List[str] = []
    if header:
        lines.append(header)
        lines.append("")
    lines.extend(
        [
            f"🎭 **{mode.get('name', 'Sem nome')}**",
            f"ID: {mode.get('id', 'N/A')}",
            f"Padrão: {mode.get('is_default', False)}",
        ]
    )
    if mode.get("description"):
        lines.append(f"Descrição: {mode['description']}")
    return "\n".join(lines)


def _format_rule(rule: Dict[str, Any], header: Optional[str] = None) -> str:
    lines: List[str] = []
    if header:
        lines.append(header)
        lines.append("")
    lines.extend(
        [
            f"📋 **{rule.get('name', 'Sem nome')}**",
            f"ID: {rule.get('id', 'N/A')}",
            f"Padrão: {rule.get('is_default', False)}",
        ]
    )
    if rule.get("description"):
        lines.append(f"Descrição: {rule['description']}")
    return "\n".join(lines)


def _format_doc(doc: Dict[str, Any], header: Optional[str] = None) -> str:
    lines: List[str] = []
    if header:
        lines.append(header)
        lines.append("")
    lines.extend(
        [
            f"📄 **{doc.get('title') or doc.get('name', 'Sem título')}**",
            f"ID: {doc.get('id', 'N/A')}",
            f"Status: {doc.get('status', 'N/A')}",
            f"Time: {doc.get('team_id', 'N/A')}",
        ]
    )
    if doc.get("updated_at") or doc.get("updatedAt"):
        lines.append(
            f"Atualizado em: {_format_date(doc.get('updated_at') or doc.get('updatedAt'))}"
        )
    return "\n".join(lines)


__all__ = ["KnowledgeTool", "KnowledgeAction"]
