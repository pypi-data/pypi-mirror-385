# SPDX-License-Identifier: Apache-2.0.
# Copyright (c) 2024 - 2025 Waldiez and contributors.

"""Exporting group chat utils.

Using the group patterns (no group manager agent)
"""

import json

from waldiez.models import WaldiezGroupManager

from .common import get_event_handler_string


def export_group_chats(
    agent_names: dict[str, str],
    manager: WaldiezGroupManager,
    initial_chat: str | None,
    tabs: int,
    is_async: bool,
) -> str:
    """Get the group chat string.

    Parameters
    ----------
    agent_names : dict[str, str]
        The agent names.
    manager : WaldiezGroupManager
        The group manager agent.
    initial_chat : str | None
        The initial chat to use if any.
    tabs : int
        The number of tabs for indentation.
    is_async : bool
        Whether the chat is asynchronous.

    Returns
    -------
    tuple[str, str]
        The group chat string and the import string.
    """
    space = "    " * tabs
    run_group_chat: str = "run_group_chat"
    if is_async:
        run_group_chat = "await a_run_group_chat"
    manager_name = agent_names[manager.id]
    pattern_name = f"{manager_name}_pattern"
    content = f"{space}results = {run_group_chat}(" + "\n"
    content += f"{space}    pattern={pattern_name}," + "\n"
    if initial_chat:
        content += f"{space}    messages={json.dumps(initial_chat)}," + "\n"
    else:
        content += f'{space}    messages="",\n'
    content += f"{space}    max_rounds={manager.data.max_round},\n"
    content += f"{space})\n"
    content += get_event_handler_string(space=space, is_async=is_async)
    return content
