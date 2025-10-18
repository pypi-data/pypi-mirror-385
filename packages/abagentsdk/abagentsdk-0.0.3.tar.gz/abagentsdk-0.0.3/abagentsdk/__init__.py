import os
import logging

# --- Silence Gemini / gRPC / absl warnings globally ---

# must be set before grpc or google libs load
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GRPC_SUPPRESS_LOGS"] = "1"
os.environ["GLOG_minloglevel"] = "3"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# silence python warnings too
logging.getLogger("absl").setLevel(logging.ERROR)
logging.getLogger("grpc").setLevel(logging.ERROR)
logging.getLogger().setLevel(logging.ERROR)

# abagentsdk/__init__.py
"""
ABZ Agent SDK — Simplify building AI Agents with Google Gemini.

Public API:
    from abagentsdk import Agent, Memory, function_tool
"""


# ─────────────────────────────────────────────
# Silence gRPC / absl / TensorFlow warnings early



# ─────────────────────────────────────────────
# Core public imports
# ─────────────────────────────────────────────
from .core.agent import Agent, AgentResult
from .core.memory import Memory
from .core.tools import Tool, ToolCall, function_tool

# Optional: expose SDK config and provider
from .config import SDKConfig
from .providers.gemini import GeminiProvider


# ─────────────────────────────────────────────
# Metadata
# ─────────────────────────────────────────────
__all__ = [
    "Agent",
    "AgentResult",
    "Memory",
    "Tool",
    "ToolCall",
    "function_tool",
    "SDKConfig",
    "GeminiProvider",
]

__version__ = "0.8.9"
__author__ = "Abu Bakar"
__license__ = "MIT"

# ─────────────────────────────────────────────
# Friendly startup banner (optional)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print(f"ABZ Agent SDK v{__version__} — Build AI Agents with Gemini")
