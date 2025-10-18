import os

from autogen_core.models import ModelFamily
from dotenv import load_dotenv

load_dotenv()

SAPTIVA_BASE_URL = "https://api.saptiva.com/v1"
SAPTIVA_API_KEY = os.getenv('SAPTIVA_API_KEY', None)
SAPTIVA_TURBO = "Saptiva Turbo"
SAPTIVA_CORTEX = "Saptiva Cortex"
SAPTIVA_LEGACY = "Saptiva Legacy"
SAPTIVA_OPS = "Saptiva Ops"
SAPTIVA_CODER = "Saptiva Coder"
SAPTIVA_OCR = "Saptiva OCR"
SAPTIVA_EMBED = "Saptiva Embed"
SAPTIVA_GUARD = "Saptiva Guard"
SAPTIVA_MULTIMODAL = "Saptiva Multimodal"
TEXT_MODEL_LIST = [SAPTIVA_LEGACY, SAPTIVA_OPS, SAPTIVA_CORTEX, SAPTIVA_TURBO]
MULTIMODAL_MODEL_LIST = [SAPTIVA_MULTIMODAL, SAPTIVA_OCR]
DEFAULT_EMBED_MODELS = [SAPTIVA_EMBED, "Qwen3-Embedding:8b"]

DEFAULT_GUARD = False
DEFAULT_LANG = 'es'
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9
DEFAULT_SEED = 42
CONTENT_CHARS_MAX = 600
CONTEXT_MAX_ITEMS = 10
SYSTEM_PROMPT = (f"Eres un asistente de inteligencia artificial experto y servicial. Puedes llamar 'tools' "
                 f"para ayudar al usuario.")
DEFAULT_MODEL_INFO = {
    "vision": True,
    "function_calling": True,
    "json_output": True,
    "family": ModelFamily.UNKNOWN,
    "structured_output": True,
    "multiple_system_messages": True
}

# Logs Constants
ROOT_LOGGER_NAME = "saptiva_agents.core"
"""str: Logger name used for structured event logging"""

EVENT_LOGGER_NAME = "saptiva_agents.core.events"
"""str: Logger name used for structured event logging"""

TRACE_LOGGER_NAME = "saptiva_agents.core.trace"
"""str: Logger name used for developer intended trace logging. The content and format of this log should not be depended upon."""

JSON_DATA_CONTENT_TYPE = "application/json"
"""JSON data content type"""

# TODO: what's the correct content type? There seems to be some disagreement over what it should be
PROTOBUF_DATA_CONTENT_TYPE = "application/x-protobuf"
"""Protobuf data content type"""