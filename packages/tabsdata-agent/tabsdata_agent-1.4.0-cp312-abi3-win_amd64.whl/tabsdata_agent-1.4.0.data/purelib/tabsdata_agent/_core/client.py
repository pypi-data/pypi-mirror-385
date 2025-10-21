#
# Copyright 2025 Tabs Data Inc.
#

import argparse
import logging
import sys
from dataclasses import dataclass
from typing import Dict, Optional

import yaml

from tabsdata.api.apiserver import APIServer
from tabsdata.api.tabsdata_server import TabsdataServer
from tabsdata_agent._core.constants import (
    AI_PROVIDERS,
    DEFAULT_AGENT_PORT,
    PORT,
    READ_ONLY,
)

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent",
        description="Tabsdata AI Agent",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--cli",
        action="store_true",
        help="Start in interactive CLI mode (default)",
    )
    group.add_argument(
        "--server",
        action="store_true",
        help="Start in server mode",
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Port to use for the agent server mode (only used with --server)",
    )
    parser.add_argument(
        "--logs-folder",
        type=str,
        help="Path of the folder where the logs of the execution are stored.",
        default=None,
    )
    parser.add_argument(
        "--log-config-file",
        type=str,
        required=True,
        help="Path of the log configuration descriptor.",
    )
    return parser


@dataclass
class Config:
    cli: bool
    server: bool
    port: int
    read_only: bool
    logs_folder: Optional[str]
    log_config_file: str
    ai_providers: Optional[Dict]


def parse_config(argv=None) -> Config:
    parser = build_parser()
    args = parser.parse_args(argv)

    raw_state = sys.stdin.read()
    ai_providers = None
    read_only = False
    port = args.port
    if raw_state:
        ai_providers_dict = yaml.safe_load(raw_state)
        ai_providers = ai_providers_dict.get(AI_PROVIDERS)
        read_only = ai_providers_dict.get(READ_ONLY, read_only)
        port = port or ai_providers_dict.get(PORT, DEFAULT_AGENT_PORT)

    cli = args.cli
    server = args.server
    if not cli and not server:
        server = True
        cli = False

    if cli and hasattr(args, "port") and args.port != DEFAULT_AGENT_PORT:
        logger.warning("Argument --port is ignored in CLI mode")

    return Config(
        cli=cli,
        server=server,
        port=port,
        read_only=read_only,
        logs_folder=args.logs_folder,
        log_config_file=args.log_config_file,
        ai_providers=ai_providers,
    )


@dataclass
class AuthConfig:
    server_address: str
    access_token: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None


class TabsdataClientFactory:
    @staticmethod
    def from_auth(auth: AuthConfig) -> TabsdataServer:
        if auth.access_token:
            try:
                connection = APIServer(auth.server_address)
                connection.bearer_token = auth.access_token
                tabsdata_server = TabsdataServer.__new__(TabsdataServer)
                tabsdata_server.connection = connection
                return tabsdata_server
            except Exception as exc:
                raise RuntimeError(f"Invalid token provided: {exc}")
        if auth.user and auth.password and auth.role:
            return TabsdataServer(
                auth.server_address, auth.user, auth.password, auth.role
            )
        raise RuntimeError(
            "Missing credentials. Provide server_address and token or"
            " user/password/role."
        )
