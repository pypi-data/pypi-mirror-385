#
# Copyright 2025 Tabs Data Inc.
#

import os
from pathlib import Path

import yaml

import tabsdata_agent

DEFAULT_SERVER_URL = "127.0.0.1:2457"
DEFAULT_MAX_ITERATIONS = 20
DEFAULT_AGENT_PORT = 2459

AI_PROVIDERS = "ai_providers"
AI_PROVIDER_API_KEY = "api_key"
AI_PROVIDER_OPENAI = "openai"
READ_ONLY = "read_only"
PORT = "port"

pacakge_root = Path(tabsdata_agent.__file__).resolve().parent

resources_folder = os.path.join(
    pacakge_root,
    "resources",
)

registry_folder = os.path.join(resources_folder, "registry")
registry_supported_folder = os.path.join(registry_folder, "supported")
registry_status_folder = os.path.join(registry_folder, "status")
registry_prompts_folder = os.path.join(registry_folder, "prompts")

system_prompt_file = os.path.join(registry_prompts_folder, "system_prompt.txt")
rag_prompt_file = os.path.join(registry_prompts_folder, "rag_prompt.txt")

faiss_folder = os.path.join(resources_folder, "faiss")
faiss_index_folder = faiss_folder


# Load all YAML files in the registry directory into a dictionary at import time
# noinspection DuplicatedCode
registry_status_content = {}
for file in os.listdir(registry_status_folder):
    if file.endswith(".yaml"):
        fpath = os.path.join(registry_status_folder, file)
        with open(fpath, "r", encoding="utf-8") as f:
            registry_status_content[os.path.splitext(file)[0]] = yaml.safe_load(f)
