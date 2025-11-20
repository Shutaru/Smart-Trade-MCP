"""Smart Trade MCP - Core business logic."""

from .config import settings
from .database import DatabaseManager
from .data_manager import DataManager

__version__ = "0.1.0"
__all__ = ["settings", "DatabaseManager", "DataManager"]
