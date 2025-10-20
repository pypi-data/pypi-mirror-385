# SPDX-License-Identifier: MIT
"""User configuration tool implementation."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from fenix_mcp.application.presenters import text
from fenix_mcp.application.tool_base import Tool, ToolRequest
from fenix_mcp.domain.user_config import UserConfigService, _strip_none
from fenix_mcp.infrastructure.context import AppContext


class UserConfigAction(str, Enum):
    def __new__(cls, value: str, description: str):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    CREATE = ("create", "Cria um novo user core document.")
    LIST = ("list", "Lista documentos com paginação opcional.")
    GET = ("get", "Obtém detalhes de um documento específico.")
    UPDATE = ("update", "Atualiza campos de um documento existente.")
    DELETE = ("delete", "Remove um documento.")
    HELP = ("help", "Mostra as ações disponíveis e seus usos.")

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


ACTION_FIELD_DESCRIPTION = "Ação a executar. Escolha um dos valores: " + ", ".join(
    f"`{member.value}` ({member.description.rstrip('.')})."
    for member in UserConfigAction
)


class UserConfigRequest(ToolRequest):
    action: UserConfigAction = Field(description=ACTION_FIELD_DESCRIPTION)
    id: Optional[str] = Field(default=None, description="ID do documento.")
    name: Optional[str] = Field(default=None, description="Nome do documento.")
    content: Optional[str] = Field(
        default=None, description="Conteúdo em Markdown/JSON."
    )
    mode_id: Optional[str] = Field(default=None, description="ID do modo associado.")
    is_default: Optional[bool] = Field(
        default=None, description="Marca o documento como padrão."
    )
    limit: int = Field(default=20, ge=1, le=100, description="Limite para listagem.")
    offset: int = Field(default=0, ge=0, description="Offset para listagem.")
    return_content: Optional[bool] = Field(
        default=None, description="Retorna conteúdo completo."
    )


class UserConfigTool(Tool):
    name = "user_config"
    description = "Gerencia documentos de configuração do usuário (Core Documents)."
    request_model = UserConfigRequest

    def __init__(self, context: AppContext):
        self._context = context
        self._service = UserConfigService(context.api_client)

    async def run(self, payload: UserConfigRequest, context: AppContext):
        action = payload.action
        if action is UserConfigAction.HELP:
            return await self._handle_help()
        if action is UserConfigAction.CREATE:
            if not payload.name or not payload.content:
                return text("❌ Informe name e content para criar o documento.")
            doc = await self._service.create(
                _strip_none(
                    {
                        "name": payload.name,
                        "content": payload.content,
                        "mode_id": payload.mode_id,
                        "is_default": payload.is_default,
                    }
                )
            )
            return text(_format_doc(doc, header="✅ Documento criado"))

        if action is UserConfigAction.LIST:
            docs = await self._service.list(
                limit=payload.limit,
                offset=payload.offset,
                returnContent=payload.return_content,
            )
            if not docs:
                return text("📂 Nenhum documento encontrado.")
            body = "\n\n".join(_format_doc(doc) for doc in docs)
            return text(f"📂 **Documentos ({len(docs)}):**\n\n{body}")

        if action is UserConfigAction.GET:
            if not payload.id:
                return text("❌ Informe o ID do documento.")
            doc = await self._service.get(
                payload.id,
                returnContent=payload.return_content,
            )
            return text(_format_doc(doc, header="📂 Detalhes do documento"))

        if action is UserConfigAction.UPDATE:
            if not payload.id:
                return text("❌ Informe o ID do documento para atualizar.")
            data = _strip_none(
                {
                    "name": payload.name,
                    "content": payload.content,
                    "mode_id": payload.mode_id,
                    "is_default": payload.is_default,
                }
            )
            doc = await self._service.update(payload.id, data)
            return text(_format_doc(doc, header="✅ Documento atualizado"))

        if action is UserConfigAction.DELETE:
            if not payload.id:
                return text("❌ Informe o ID do documento.")
            await self._service.delete(payload.id)
            return text(f"🗑️ Documento {payload.id} removido.")

        return text(
            "❌ Ação de user_config não suportada.\n\nEscolha um dos valores:\n"
            + "\n".join(f"- `{value}`" for value in UserConfigAction.choices())
        )

    async def _handle_help(self):
        return text(
            "📚 **Ações disponíveis para user_config**\n\n"
            + UserConfigAction.formatted_help()
        )


def _format_doc(doc: Dict[str, Any], header: Optional[str] = None) -> str:
    lines: List[str] = []
    if header:
        lines.append(header)
        lines.append("")
    lines.extend(
        [
            f"📂 **{doc.get('name', 'Sem nome')}**",
            f"ID: {doc.get('id', 'N/A')}",
            f"Default: {doc.get('is_default', False)}",
        ]
    )
    if doc.get("mode_id"):
        lines.append(f"Modo associado: {doc['mode_id']}")
    if doc.get("content") and len(doc["content"]) <= 400:
        lines.append("")
        lines.append(doc["content"])
    return "\n".join(lines)
