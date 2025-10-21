# -*- coding: utf-8 -*-
"""MCP Gateway LLMGuardPlugin Plugin - A plugin that leverages the capabilities of llmguard library to apply guardrails on input and output prompts.

Copyright 2025
SPDX-License-Identifier: Apache-2.0
Authors: Shriti Priya

"""

import importlib.metadata

# Package version
try:
    __version__ = importlib.metadata.version("llmguardplugin")
except Exception:
    __version__ = "0.1.0"

__author__ = "Shriti Priya"
__copyright__ = "Copyright 2025"
__license__ = "Apache 2.0"
__description__ = "A plugin that leverages the capabilities of llmguard library to apply guardrails on input and output prompts"
__url__ = "https://ibm.github.io/mcp-context-forge/"
__download_url__ = "https://github.com/IBM/mcp-context-forge"
__packages__ = ["llmguardplugin"]
