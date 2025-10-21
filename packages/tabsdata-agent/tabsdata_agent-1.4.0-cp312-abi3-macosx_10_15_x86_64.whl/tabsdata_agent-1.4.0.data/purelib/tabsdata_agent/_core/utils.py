#
# Copyright 2025 Tabs Data Inc.
#

import json

import tiktoken
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

from tabsdata.api.tabsdata_server import TabsdataServer


def get_client(config: RunnableConfig) -> TabsdataServer:
    """
    Get a TabsdataServer client from a RunnableConfig.
    """
    client = config["configurable"].get("tabsdata", None)
    if client and isinstance(client, TabsdataServer):
        return client
    else:
        raise ValueError("TabsdataServer client not found in config.")


def extract_tools(chat_response: dict) -> list[tuple[str, dict]]:
    """
    Extract tool names called (tool_calls) in a LangChain chat response.
    Returns a list of tuples (tool_name, arguments_dict).
    """
    tools_used_with_args = []

    for msg in reversed(chat_response.get("messages", [])):
        if isinstance(msg, AIMessage):
            for call in msg.additional_kwargs.get("tool_calls", []):
                # LangChain stores tool name and arguments under 'function'
                if "function" in call:
                    tool_name = call["function"].get("name")
                    arguments = call["function"].get("arguments", {})
                    # arguments are usually a JSON string, parse if needed
                    try:
                        arguments = (
                            json.loads(arguments)
                            if isinstance(arguments, str)
                            else arguments
                        )
                    except json.JSONDecodeError:
                        pass
                    tools_used_with_args.append((tool_name, arguments))
    return tools_used_with_args


def extract_final_answer(chat_response: dict) -> str:
    """
    Extract the final answer from a LangChain chat response.
    Returns the content of the last AIMessage.
    """
    for msg in reversed(chat_response.get("messages", [])):
        if isinstance(msg, AIMessage):
            return msg.content
    if "error" in chat_response:
        return chat_response["error"]
    return ""


def count_tokens(chat_response: dict, model: str = "gpt-4") -> int:
    """
    Approximate token count for a LangChain chat response using tiktoken.
    It only counts the tokens in the messages.
    """
    messages = chat_response.get("messages", [])
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(str(messages))
    return len(tokens)
