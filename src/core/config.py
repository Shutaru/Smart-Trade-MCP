"""Configuration management using Pydantic Settings."""

from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # MCP Server
    mcp_server_name: str = Field(default="smart-trade-mcp")
    mcp_server_version: str = Field(default="0.1.0")
    log_level: str = Field(default="INFO")

    # Trading
    exchange: str = Field(default="binance")
    testnet: bool = Field(default=True)
    dry_run: bool = Field(default=True)

    # API Keys
    binance_api_key: Optional[str] = Field(default=None)
    binance_secret_key: Optional[str] = Field(default=None)

    # Database
    database_url: str = Field(default="sqlite+aiosqlite:///data/smart_trade.db")

    # Optimization
    max_workers: int = Field(default=4, ge=1, le=32)
    gpu_enabled: bool = Field(default=False)
    gpu_device_ids: str = Field(default="0")

    # Meta-Learning
    ml_model_path: Path = Field(default=Path("data/ml/meta_learner.pt"))
    ml_enabled: bool = Field(default=True)

    # Risk Management
    max_position_size: float = Field(default=0.1, ge=0.01, le=1.0)
    max_drawdown: float = Field(default=0.2, ge=0.05, le=0.5)
    stop_loss_pct: float = Field(default=0.05, ge=0.01, le=0.2)

    # Backtesting
    backtest_start_date: str = Field(default="2023-01-01")
    backtest_end_date: str = Field(default="2024-01-01")
    initial_capital: float = Field(default=10000.0, gt=0)

    # Agent
    agent_max_iterations: int = Field(default=100, ge=1, le=1000)
    agent_loop_detection_threshold: int = Field(default=3, ge=2, le=10)
    workflow_enforcement: bool = Field(default=True)

    @field_validator("gpu_device_ids")
    @classmethod
    def parse_gpu_ids(cls, v: str) -> str:
        """Validate GPU device IDs format."""
        if not all(x.strip().isdigit() for x in v.split(",")):
            raise ValueError("GPU device IDs must be comma-separated integers")
        return v

    @property
    def gpu_devices(self) -> List[int]:
        """Get list of GPU device IDs."""
        return [int(x.strip()) for x in self.gpu_device_ids.split(",")]

    def is_valid_api_key(self) -> bool:
        """Check if API keys are valid (not placeholder values)."""
        if not self.binance_api_key or not self.binance_secret_key:
            return False

        # Check for placeholder values
        placeholder_values = ["your_api_key_here", "your_secret_key_here", ""]

        if self.binance_api_key in placeholder_values:
            return False
        if self.binance_secret_key in placeholder_values:
            return False

        return True


# Singleton instance
settings = Settings()
