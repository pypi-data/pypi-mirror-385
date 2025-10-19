# SPDX-License-Identifier: Apache-2.0.
# Copyright (c) 2024 - 2025 Waldiez and contributors.
"""Get pgvector related content and imports."""

from waldiez.models import WaldiezRagUserProxy


def _get_pgvector_client_string(agent: WaldiezRagUserProxy) -> tuple[str, str]:
    """Get the PGVectorDB client string.

    Parameters
    ----------
    agent : WaldiezRagUserProxy
        The agent.

    Returns
    -------
    tuple[str, str]
        The 'client' and what to import.
    """
    to_import = "import psycopg"
    client_str = "psycopg."
    connection_url = agent.retrieve_config.db_config.connection_url
    client_str += f'connect("{connection_url}")'
    return client_str, to_import


def _get_pgvector_embedding_function_string(
    agent: WaldiezRagUserProxy, agent_name: str
) -> tuple[str, str, str]:
    """Get the PGVectorDB embedding function string.

    Parameters
    ----------
    agent : WaldiezRagUserProxy
        The agent.
    agent_name : str
        The agent's name.

    Returns
    -------
    tuple[str, str, str]
        The 'embedding_function', the import and the custom_embedding_function.
    """
    to_import = ""
    embedding_function_content = ""
    if agent.retrieve_config.use_custom_embedding:
        embedding_function_content, embedding_function_arg = (
            agent.retrieve_config.get_custom_embedding_function(
                name_suffix=agent_name
            )
        )
        embedding_function_content = "\n" + embedding_function_content
    else:
        to_import = "from sentence_transformers import SentenceTransformer"
        embedding_function_arg = "SentenceTransformer("
        embedding_function_arg += (
            f'"{agent.retrieve_config.db_config.model}").encode'
        )
    return embedding_function_arg, to_import, embedding_function_content


def get_pgvector_db_args(
    agent: WaldiezRagUserProxy, agent_name: str
) -> tuple[str, set[str], str]:
    """Get the kwargs to use for PGVectorDB.

    Parameters
    ----------
    agent : WaldiezRagUserProxy
        The agent.
    agent_name : str
        The agent's name.

    Returns
    -------
    tuple[tuple[str,str], Set[str], str]
        The kwargs to use, what to import and the custom_embedding_function.
    """
    client_str, to_import_client = _get_pgvector_client_string(agent)
    embedding_function_arg, to_import_embedding, embedding_function_body = (
        _get_pgvector_embedding_function_string(agent, agent_name)
    )
    to_import = (
        {to_import_client, to_import_embedding}
        if to_import_embedding
        else {to_import_client}
    )
    kwarg_str = (
        f"            client={client_str},"
        "\n"
        f"            embedding_function={embedding_function_arg},"
        "\n"
    )
    return kwarg_str, to_import, embedding_function_body
