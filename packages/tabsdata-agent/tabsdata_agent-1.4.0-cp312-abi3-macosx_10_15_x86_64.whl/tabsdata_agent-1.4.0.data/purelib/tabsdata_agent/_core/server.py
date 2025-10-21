#
# Copyright 2025 Tabs Data Inc.
#

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel

import tabsdata_agent
from tabsdata._tabsserver.function.global_utils import setup_logging
from tabsdata_agent._core.agent import TabsdataAgentFactory
from tabsdata_agent._core.client import AuthConfig, TabsdataClientFactory, parse_config
from tabsdata_agent._core.constants import (
    AI_PROVIDER_OPENAI,
    DEFAULT_AGENT_PORT,
    DEFAULT_MAX_ITERATIONS,
)
from tabsdata_agent._core.tools.tabsdata import ReadWriteMode
from tabsdata_agent._core.utils import extract_final_answer, extract_tools

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str
    auth: AuthConfig
    thread_id: str = None
    ai_provider: str = AI_PROVIDER_OPENAI


class TabsdataAgent:
    def __init__(
        self, read_only: bool, cli: bool, port: int, agent_factory: TabsdataAgentFactory
    ):
        self.name = "Tabsdata Agent"
        self.version = tabsdata_agent.version
        self.port = port
        self.read_only = read_only
        self.cli = cli
        self.agent_factory = agent_factory
        self.agent_executors = agent_factory.load_agent_executors()
        logger.info(f"Available AI executors: {list(self.agent_executors.keys())}")
        if not self.agent_executors:
            raise RuntimeError("No agent executors available.")

    def chat(self, req: ChatRequest):
        logger.info(f"{req.thread_id}: Request started.")

        # setup client
        try:
            client = TabsdataClientFactory.from_auth(req.auth)
        except Exception as e:
            logger.error(f"{req.thread_id}: Authentication failed: {e}")
            return {"error": "Authentication to Tabsdata failed", "messages": []}

        # config for this run
        config = RunnableConfig(
            recursion_limit=DEFAULT_MAX_ITERATIONS,
            configurable={
                "tabsdata": client,
                **({"thread_id": req.thread_id} if req.thread_id else {}),
            },
        )

        # get executor for the requested AI provider
        executor = self.agent_executors.get(req.ai_provider)
        if executor is None:
            logger.error(
                f"{req.thread_id}: AI provider '{req.ai_provider}' not supported"
            )
            return {
                "error": f"AI provider '{req.ai_provider}' not supported",
                "messages": [],
            }

        # setup agent run
        messages = [{"role": "user", "content": req.message}]
        try:
            response = executor.invoke(
                {"messages": messages}, config, stream_mode="values"
            )
        except Exception as e:
            logger.error(f"{req.thread_id}: Agent stopped due to: {e}")
            # Try to get partial output if available
            return {"error": str(e), "messages": messages}

        # Parse final response explicitly, and leave rest of the response as-is.
        final_answer = extract_final_answer(response)

        logger.info(f"{req.thread_id}: Request finished")
        return {"response": final_answer, **response}

    def _run_cli(self):
        print("Type 'exit' to quit.")
        thread_id = "cli-session"
        # default auth for local testing
        auth = AuthConfig(
            server_address="http://localhost:2457",
            access_token=None,
            user="admin",
            password="tabsdata",
            role="sys_admin",
        )
        while True:
            try:
                user_input = input("You: ")
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                break
            if user_input.strip().lower() in ("exit", "quit"):
                print("Exiting.")
                break
            req = ChatRequest(message=user_input, auth=auth, thread_id=thread_id)
            result = self.chat(req)
            response = extract_final_answer(result)
            tools_used = extract_tools(result)
            print(f"Agent response:\n {response}\n")
            print("--------------------------------\n")
            print(f"Tools used: {tools_used}\n")

    def _run_server(self):
        @asynccontextmanager
        async def lifespan(_app: FastAPI):
            # Startup
            logger.info(f"Starting agent server on port {self.port}...")
            yield
            # Shutdown
            logger.info("Received termination signal. Shutting down gracefully...")

        app = FastAPI(lifespan=lifespan)

        @app.post("/chat")
        async def chat_endpoint(req: ChatRequest):
            return self.chat(req)

        logger.info(f"Initializing agent server on port {self.port}...")
        import uvicorn

        uvicorn.run(app=app, host="0.0.0.0", port=self.port)

    def run(self):
        logger.info(f"{self.name} v{self.version}")
        if self.cli:
            self._run_cli()
        else:
            self._run_server()


def main(argv=None):
    config = parse_config(argv)

    logs_folder = config.logs_folder
    log_config_file = config.log_config_file
    setup_logging(
        default_path=log_config_file,
        logs_folder=logs_folder,
    )
    global logger
    logger = logging.getLogger(__name__)

    logger.info("Starting Tabsdata Agent...")
    if not config.ai_providers:
        logger.error("No AI provider configured. Exiting.")
        exit(0)

    agent_factory = TabsdataAgentFactory(
        mode=ReadWriteMode.READ if config.read_only else ReadWriteMode.READWRITE,
        ai_providers=config.ai_providers,
    )

    logger.info(f"Configured AI providers: {list(config.ai_providers.keys())}")
    agent_factory.load_agent_executors()
    logger.info(
        f"Loaded agent executors: {list(agent_factory.agent_executors.keys())}",
    )

    if not agent_factory.agent_executors:
        logger.error("No agent executors available. Exiting.")
        exit(0)

    logger.info("Starting Tabsdata agent...")
    agent = TabsdataAgent(
        read_only=config.read_only,
        cli=config.cli,
        port=config.port if config.server else DEFAULT_AGENT_PORT,
        agent_factory=agent_factory,
    )
    agent.run()
    exit(0)


if __name__ == "__main__":
    main()
