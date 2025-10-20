# SPDX-License-Identifier: MIT
"""Initialization tool implementation."""

from __future__ import annotations

from enum import Enum
import json
from typing import List, Optional

from pydantic import Field

from fenix_mcp.application.presenters import text
from fenix_mcp.application.tool_base import Tool, ToolRequest
from fenix_mcp.domain.initialization import InitializationService
from fenix_mcp.infrastructure.context import AppContext


class InitializeAction(str, Enum):
    INIT = "init"
    SETUP = "setup"


class InitializeRequest(ToolRequest):
    action: InitializeAction = Field(
        description="Operação de inicialização a executar."
    )
    include_user_docs: bool = Field(
        default=True,
        description=(
            "Inclui documentos pessoais durante a inicialização "
            "(apenas para ação init)."
        ),
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=200,
        description=("Quantidade máxima de documentos principais/pessoais carregados."),
    )
    answers: Optional[List[str]] = Field(
        default=None,
        description=(
            "Lista com 9 respostas textuais para processar o setup personalizado."
        ),
    )


class InitializeTool(Tool):
    name = "initialize"
    description = (
        "Inicializa o ambiente do Fênix Cloud ou processa o setup personalizado."
    )
    request_model = InitializeRequest

    def __init__(self, context: AppContext):
        self._context = context
        self._service = InitializationService(context.api_client, context.logger)

    async def run(self, payload: InitializeRequest, context: AppContext):
        if payload.action is InitializeAction.INIT:
            return await self._handle_init(payload)
        if payload.action is InitializeAction.SETUP:
            return await self._handle_setup(payload)
        return text("❌ Ação de inicialização desconhecida.")

    async def _handle_init(self, payload: InitializeRequest):
        try:
            data = await self._service.gather_data(
                include_user_docs=payload.include_user_docs,
                limit=payload.limit,
            )
        except Exception as exc:  # pragma: no cover - defensive
            self._context.logger.error("Initialize failed: %s", exc)
            return text(
                "❌ Falha ao carregar dados de inicialização. "
                "Verifique se o token tem acesso à API."
            )

        if (
            not data.core_documents
            and (not data.user_documents or not payload.include_user_docs)
            and not data.profile
        ):
            return text(
                "⚠️ Não consegui carregar documentos nem perfil. Confirme o token e, se for o primeiro acesso, use `initialize action=setup` para responder ao questionário inicial."
            )

        payload_dict = {
            "profile": data.profile,
            "core_documents": data.core_documents,
            "user_documents": data.user_documents if payload.include_user_docs else [],
        }
        if data.recent_memories:
            payload_dict["recent_memories"] = data.recent_memories

        message_lines = [
            "📦 **Dados de inicialização completos**",
            "```json",
            json.dumps(payload_dict, ensure_ascii=False, indent=2),
            "```",
        ]

        if payload.include_user_docs and not data.user_documents and data.profile:
            message_lines.extend(
                [
                    "",
                    self._service.build_new_user_prompt(data),
                ]
            )

        return text("\n".join(message_lines))

    async def _handle_setup(self, payload: InitializeRequest):
        answers = payload.answers or []
        validation_error = self._service.validate_setup_answers(answers)
        if validation_error:
            return text(f"❌ {validation_error}")

        summary_lines = [
            "📝 **Setup personalizado recebido!**",
            "",
            "Suas respostas foram registradas. Vou sugerir documentos, regras e rotinas com base nessas informações.",
            "",
            "Resumo das respostas:",
        ]
        for idx, answer in enumerate(answers, start=1):
            summary_lines.append(f"{idx}. {answer.strip()}")

        summary_lines.extend(
            [
                "",
                "Agora você pode pedir conteúdos específicos, por exemplo:",
                "- `productivity action=todo_create ...`",
                "- `knowledge action=mode_list`",
            ]
        )

        return text("\n".join(summary_lines))
