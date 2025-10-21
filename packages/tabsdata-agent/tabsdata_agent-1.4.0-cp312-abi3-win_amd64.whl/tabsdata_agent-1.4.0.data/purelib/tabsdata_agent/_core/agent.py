#
# Copyright 2025 Tabs Data Inc.
#

import logging
import sqlite3

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import RemoveMessage, trim_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.prebuilt import create_react_agent

from tabsdata_agent._core.constants import (
    AI_PROVIDER_API_KEY,
    AI_PROVIDER_OPENAI,
    system_prompt_file,
)
from tabsdata_agent._core.tools.rag import RagToolFactory
from tabsdata_agent._core.tools.tabsdata import ReadWriteMode, TabsdataToolsFactory

logger = logging.getLogger(__name__)


class TabsdataAgentFactory:
    def __init__(
        self,
        mode: ReadWriteMode,
        ai_providers: dict[str, dict],
        prompt=None,
        memory_saver=None,
        auth_config=None,
        rag_tool_kwargs=None,
    ):
        self.mode = mode
        self.ai_providers = ai_providers
        self.prompt = prompt or self._load_system_prompt()
        self.memory_saver = memory_saver or self._load_memory_saver()
        self.auth_config = auth_config
        self.rag_tool_kwargs = rag_tool_kwargs or {}
        self.agent_executors = {}

    @staticmethod
    def _load_memory_saver():
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        return SqliteSaver(conn)

    @staticmethod
    def _load_system_prompt():
        try:
            with open(system_prompt_file, "r", encoding="utf-8") as _f:
                prompt = _f.read()
        except Exception as e:
            logger.error(
                f"Error: could not read system prompt file: {system_prompt_file}: {e}",
            )
            raise e
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("System prompt file is empty")
        return prompt

    def create_agent_executor(self, llm: BaseLanguageModel, embeddings: Embeddings):
        tabsdata_tools = TabsdataToolsFactory(mode=self.mode).get_tools()
        # we could have a different llm and embeddings for RAG if needed
        rag_tool = RagToolFactory(
            llm=llm, embeddings=embeddings, **self.rag_tool_kwargs
        ).get_tool()
        tools = tabsdata_tools + [rag_tool]

        def pre_model_hook(state):
            # Keeping latest messages by token count (for now)
            trimmed = trim_messages(
                state["messages"],
                max_tokens=4096,
                allow_partial=False,
                strategy="last",
                token_counter=llm,
                start_on="human",
                end_on=("human", "tool"),
            )
            return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *trimmed]}

        agent_executor = create_react_agent(
            model=llm,
            tools=tools,
            prompt=self.prompt,
            checkpointer=self.memory_saver,
            pre_model_hook=pre_model_hook,
        )
        return agent_executor

    def load_agent_executors(self):
        agent_executors = {}
        for name, provider in self.ai_providers.items():
            if name == AI_PROVIDER_OPENAI:
                from langchain_openai import ChatOpenAI, OpenAIEmbeddings

                api_key = provider.get(AI_PROVIDER_API_KEY)
                if not api_key:
                    logger.warning(
                        f"API key for AI provider '{name}' not found, skipping..."
                    )
                    continue

                llm = ChatOpenAI(
                    model="gpt-4",
                    temperature=0.1,
                    api_key=provider.get(AI_PROVIDER_API_KEY),
                )
                agent_executors[AI_PROVIDER_OPENAI] = self.create_agent_executor(
                    llm, OpenAIEmbeddings()
                )
                logger.info(f"AI provider '{name}' initialized.")
            else:
                logger.warning(f"AI provider '{name}' not supported, skipping...")
        self.agent_executors = agent_executors
        return self.agent_executors
