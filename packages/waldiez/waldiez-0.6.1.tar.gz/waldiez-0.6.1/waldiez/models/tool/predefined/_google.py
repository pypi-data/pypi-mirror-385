# SPDX-License-Identifier: Apache-2.0.
# Copyright (c) 2024 - 2025 Waldiez and contributors.
# pylint: disable=line-too-long
# flake8: noqa: E501
"""Predefined Google search tool for Waldiez."""

import os
from typing import Any

from ._config import PredefinedToolConfig
from .protocol import PredefinedTool


class GoogleSearchToolImpl(PredefinedTool):
    """Google search tool for Waldiez."""

    required_secrets: list[str] = [
        "GOOGLE_SEARCH_API_KEY",
        "GOOGLE_SEARCH_ENGINE_ID",
    ]
    required_kwargs: dict[str, type] = {}
    _kwargs: dict[str, Any] = {}

    @property
    def name(self) -> str:
        """Tool name."""
        return "google_search"

    @property
    def description(self) -> str:
        """Tool description."""
        return "Search Google for a given query."

    @property
    def kwargs(self) -> dict[str, Any]:
        """Keyword arguments for the tool, used for initialization."""
        return self._kwargs

    @property
    def requirements(self) -> list[str]:
        """Python requirements for the tool."""
        return ["ag2[google-search,gemini]"]

    @property
    def tags(self) -> list[str]:
        """Tags for the tool, used for categorization."""
        return ["google", "search", "web"]

    @property
    def tool_imports(self) -> list[str]:
        """Imports required for the tool implementation."""
        return [
            "from autogen.tools.experimental import GoogleSearchTool",
        ]

    @property
    def google_search_engine_id(self) -> str:
        """Google search engine ID."""
        from_env = os.environ.get("GOOGLE_SEARCH_ENGINE_ID", "")
        if from_env:
            return from_env
        return str(self.kwargs.get("google_search_engine_id", ""))

    def validate_secrets(self, secrets: dict[str, str]) -> list[str]:
        """Validate secrets and return list of missing required ones.

        Parameters
        ----------
        secrets : dict[str, str]
            Dictionary of secrets/environment variables.

        Returns
        -------
        list[str]
            List of missing required secrets.
        """
        missing: list[str] = []
        for secret in self.required_secrets:
            if secret not in secrets:
                missing.append(secret)
        return missing

    def validate_kwargs(self, kwargs: dict[str, str]) -> list[str]:
        """Validate keyword arguments and return list of missing required ones.

        Parameters
        ----------
        kwargs : dict[str, str]
            Dictionary of keyword arguments.

        Returns
        -------
        list[str]
            List of missing required keyword arguments.

        Raises
        ------
        ValueError
            If any keyword argument is invalid
            (cannot be cast to the required type).
        """
        missing: list[str] = []
        invalid: list[str] = []
        for name, type_of in self.required_kwargs.items():
            if name not in kwargs:
                missing.append(name)
            elif not isinstance(kwargs[name], type_of):
                # pylint: disable=broad-exception-caught
                # noinspection PyBroadException
                try:
                    kwargs[name] = type_of(kwargs[name])
                    self._kwargs[name] = kwargs[name]
                except Exception:
                    invalid.append(name)
                else:
                    if name in self._kwargs:
                        self._kwargs[name] = kwargs[name]
            else:
                self._kwargs[name] = kwargs[name]
        if invalid:
            raise ValueError(f"Invalid keyword arguments: {invalid}")
        return missing

    def get_content(
        self,
        secrets: dict[str, str],
        runtime_kwargs: dict[str, Any] | None = None,
    ) -> str:
        """Get content for the tool.

        Parameters
        ----------
        secrets : dict[str, str]
            Dictionary of secrets/environment variables.
        runtime_kwargs : dict[str, Any] | None, optional
            Runtime keyword arguments to customize the content generation.

        Returns
        -------
        str
            The content for the tool.
        """
        content = f'''
def {self.name}(
    query: str,
    num_results: int = 10,
) -> list[dict[str, Any]]:
    """Perform a Google search and return formatted results.

    Args:
        query: The search query string.
        num_results: The maximum number of results to return. Defaults to 10.
    Returns:
        A list of dictionaries of the search results.
    """
    google_search_api_key = os.environ.get("GOOGLE_SEARCH_API_KEY", "")
    if not google_search_api_key:
        raise ValueError("GOOGLE_SEARCH_API_KEY is required for Google search tool.")
    google_search_engine_id = os.environ.get("GOOGLE_SEARCH_ENGINE_ID", "")
    if not google_search_engine_id:
        raise ValueError("Google Search Engine ID is required for Google search tool.")
    {self.name}_tool = GoogleSearchTool(
        search_api_key=google_search_api_key,
        search_engine_id=google_search_engine_id,
    )
    return {self.name}_tool(
        query=query,
        search_api_key=google_search_api_key,
        search_engine_id=google_search_engine_id,
        num_results=num_results
    )
'''
        return content


# pylint: disable=invalid-name
GoogleSearchTool = GoogleSearchToolImpl()
GoogleSearchConfig = PredefinedToolConfig(
    name=GoogleSearchTool.name,
    description=GoogleSearchTool.description,
    required_secrets=GoogleSearchTool.required_secrets,
    required_kwargs=GoogleSearchTool.required_kwargs,
    requirements=GoogleSearchTool.requirements,
    tags=GoogleSearchTool.tags,
    implementation=GoogleSearchTool,
)
