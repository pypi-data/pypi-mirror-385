# SPDX-License-Identifier: Apache-2.0.
# Copyright (c) 2024 - 2025 Waldiez and contributors.
"""Waldiez Agent Nested Chat."""

from pydantic import Field
from typing_extensions import Annotated

from ...common import (
    WaldiezBase,
    WaldiezDefaultCondition,
    WaldiezHandoffCondition,
    WaldiezTransitionAvailability,
)


class WaldiezAgentNestedChatMessage(WaldiezBase):
    """Waldiez Agent nested chat message.

    A reference to a chat's message or reply in a nested chat

    Attributes
    ----------
    id : str
        The id of the chat.
    is_reply : bool
        Whether to use the reply in the chat or not.
    """

    id: Annotated[
        str, Field(..., title="ID", description="The id of the chat.")
    ]
    is_reply: Annotated[
        bool,
        Field(
            False,
            title="Is reply",
            description="Whether to use the reply in the chat or not.",
            alias="isReply",
        ),
    ]


class WaldiezAgentNestedChat(WaldiezBase):
    """Waldiez Agent Nested Chat.

    Attributes
    ----------
    triggered_by : list[str]
        A list of agent ids that trigger the nested chat.
    messages : list[WaldiezAgentNestedChatMessage]
        The list of messages (chat ids and 'is_reply'z)
        to include the in the nested chat registration.
    """

    triggered_by: Annotated[
        list[str],
        Field(
            title="Triggered By",
            description="A list of agent ids that trigger the nested chat.",
            alias="triggeredBy",
            default_factory=list,
        ),
    ]
    messages: Annotated[
        list[WaldiezAgentNestedChatMessage],
        Field(
            title="Messages",
            description=(
                "The list of messages (chat ids and 'is_reply'z)"
                "to include the in the nested chat registration."
            ),
            default_factory=list,
        ),
    ]
    condition: Annotated[
        WaldiezHandoffCondition,
        Field(
            default_factory=WaldiezDefaultCondition.create,
            title="Condition",
            description=(
                "The condition to use for the nested chat handoff. "
                "If not provided, the nested chat will always be available."
            ),
        ),
    ]
    available: Annotated[
        WaldiezTransitionAvailability,
        Field(
            default_factory=WaldiezTransitionAvailability,
            title="Available",
            description=(
                "The availability of the nested chat. "
                "If not provided, the nested chat will always be available."
            ),
        ),
    ]
