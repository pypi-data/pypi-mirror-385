#
# Copyright 2025 Tabs Data Inc.
#

import importlib.metadata

# noinspection PyBroadException
try:
    __version__ = importlib.metadata.version("tabsdata_agent")
except Exception:
    __version__ = "unknown"

version = __version__
