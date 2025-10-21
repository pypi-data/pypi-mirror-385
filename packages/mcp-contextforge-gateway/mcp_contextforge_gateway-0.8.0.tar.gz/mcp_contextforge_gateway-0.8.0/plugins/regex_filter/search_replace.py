# -*- coding: utf-8 -*-
"""Location: ./plugins/regex_filter/search_replace.py
Copyright 2025
SPDX-License-Identifier: Apache-2.0
Authors: Teryl Taylor

Simple example plugin for searching and replacing text.
This module loads configurations for plugins.
"""

# Standard
import re

# Third-Party
from pydantic import BaseModel

# First-Party
from mcpgateway.plugins.framework import (
    Plugin,
    PluginConfig,
    PluginContext,
    PromptPosthookPayload,
    PromptPosthookResult,
    PromptPrehookPayload,
    PromptPrehookResult,
    ToolPostInvokePayload,
    ToolPostInvokeResult,
    ToolPreInvokePayload,
    ToolPreInvokeResult,
)


class SearchReplace(BaseModel):
    """Search and replace pattern configuration.

    Attributes:
        search: Regular expression pattern to search for.
        replace: Replacement text.
    """

    search: str
    replace: str


class SearchReplaceConfig(BaseModel):
    """Configuration for search and replace plugin.

    Attributes:
        words: List of search and replace patterns to apply.
    """

    words: list[SearchReplace]


class SearchReplacePlugin(Plugin):
    """Example search replace plugin."""

    def __init__(self, config: PluginConfig):
        """Initialize the search and replace plugin.

        Args:
            config: Plugin configuration containing search/replace patterns.
        """
        super().__init__(config)
        self._srconfig = SearchReplaceConfig.model_validate(self._config.config)
        self.__patterns = []
        for word in self._srconfig.words:
            self.__patterns.append((r"{}".format(word.search), word.replace))

    async def prompt_pre_fetch(self, payload: PromptPrehookPayload, context: PluginContext) -> PromptPrehookResult:
        """The plugin hook run before a prompt is retrieved and rendered.

        Args:
            payload: The prompt payload to be analyzed.
            context: contextual information about the hook call.

        Returns:
            The result of the plugin's analysis, including whether the prompt can proceed.
        """
        if payload.args:
            for pattern in self.__patterns:
                for key in payload.args:
                    value = re.sub(pattern[0], pattern[1], payload.args[key])
                    payload.args[key] = value
        return PromptPrehookResult(modified_payload=payload)

    async def prompt_post_fetch(self, payload: PromptPosthookPayload, context: PluginContext) -> PromptPosthookResult:
        """Plugin hook run after a prompt is rendered.

        Args:
            payload: The prompt payload to be analyzed.
            context: Contextual information about the hook call.

        Returns:
            The result of the plugin's analysis, including whether the prompt can proceed.
        """

        if payload.result.messages:
            for index, message in enumerate(payload.result.messages):
                for pattern in self.__patterns:
                    value = re.sub(pattern[0], pattern[1], message.content.text)
                    payload.result.messages[index].content.text = value
        return PromptPosthookResult(modified_payload=payload)

    async def tool_pre_invoke(self, payload: ToolPreInvokePayload, context: PluginContext) -> ToolPreInvokeResult:
        """Plugin hook run before a tool is invoked.

        Args:
            payload: The tool payload to be analyzed.
            context: Contextual information about the hook call.

        Returns:
            The result of the plugin's analysis, including whether the tool can proceed.
        """
        if payload.args:
            for pattern in self.__patterns:
                for key in payload.args:
                    if isinstance(payload.args[key], str):
                        value = re.sub(pattern[0], pattern[1], payload.args[key])
                        payload.args[key] = value
        return ToolPreInvokeResult(modified_payload=payload)

    async def tool_post_invoke(self, payload: ToolPostInvokePayload, context: PluginContext) -> ToolPostInvokeResult:
        """Plugin hook run after a tool is invoked.

        Args:
            payload: The tool result payload to be analyzed.
            context: Contextual information about the hook call.

        Returns:
            The result of the plugin's analysis, including whether the tool result should proceed.
        """
        if payload.result and isinstance(payload.result, dict):
            for pattern in self.__patterns:
                for key in payload.result:
                    if isinstance(payload.result[key], str):
                        value = re.sub(pattern[0], pattern[1], payload.result[key])
                        payload.result[key] = value
        elif payload.result and isinstance(payload.result, str):
            for pattern in self.__patterns:
                payload.result = re.sub(pattern[0], pattern[1], payload.result)
        return ToolPostInvokeResult(modified_payload=payload)
