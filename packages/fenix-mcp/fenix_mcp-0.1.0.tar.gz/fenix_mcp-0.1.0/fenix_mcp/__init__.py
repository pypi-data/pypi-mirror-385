# SPDX-FileCopyrightText: 2024 Bruno Fernandes
# SPDX-License-Identifier: MIT

"""
Fênix Cloud MCP Server (Python edition).

This package follows a Clean Architecture layout inside the MCP ecosystem:

- interface: transports and MCP protocol glue code
- application: tools, registries, presenters and use-case orchestrators
- domain: pure business models and services
- infrastructure: API clients, config, logging and shared context
"""

__all__ = ["__version__"]

__version__ = "0.1.0"
