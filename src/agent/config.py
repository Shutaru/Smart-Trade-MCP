# -*- coding: utf-8 -*-
"""
Trading Agent Configuration

User-configurable settings for autonomous trading agent.
"""

from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class TradingPairConfig(BaseModel):
    """Configuration for a trading pair."""
    
    symbol: str = Field(..., description="Trading pair symbol (e.g., BTC/USDT)")
    timeframe: str = Field(default="1h", description="Timeframe for signals")
    enabled: bool = Field(default=True, description="Enable scanning for this pair")
    
    @validator('timeframe')
    def validate_timeframe(cls, v):
        valid = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
        if v not in valid:
            raise ValueError(f"Timeframe must be one of {valid}")
        return v


class StrategyConfig(BaseModel):
    """Configuration for a trading strategy."""
    
    name: str = Field(..., description="Strategy name")
    enabled: bool = Field(default=True, description="Enable this strategy")
    min_confidence: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum signal confidence")


class ScannerConfig(BaseModel):
    """Configuration for signal scanner."""
    
    scan_interval_minutes: int = Field(
        default=15,
        ge=1,
        le=1440,
        description="How often to scan (in minutes)"
    )
    
    lookback_candles: int = Field(
        default=500,
        ge=50,
        le=5000,
        description="Number of candles to analyze"
    )
    
    parallel_scanning: bool = Field(
        default=True,
        description="Scan pairs in parallel for speed"
    )
    
    max_workers: int = Field(
        default=4,
        ge=1,
        le=16,
        description="Number of parallel workers"
    )


class AlertConfig(BaseModel):
    """Configuration for alerts."""
    
    telegram_enabled: bool = Field(default=False, description="Enable Telegram notifications")
    telegram_bot_token: Optional[str] = Field(None, description="Telegram bot token")
    telegram_chat_id: Optional[str] = Field(None, description="Telegram chat ID")
    
    email_enabled: bool = Field(default=False, description="Enable email notifications")
    email_to: Optional[str] = Field(None, description="Email address for alerts")
    
    webhook_enabled: bool = Field(default=False, description="Enable webhook callbacks")
    webhook_url: Optional[str] = Field(None, description="Webhook URL")


class AgentConfig(BaseModel):
    """Complete trading agent configuration."""
    
    # Trading pairs to monitor
    pairs: List[TradingPairConfig] = Field(
        default_factory=lambda: [
            TradingPairConfig(symbol="BTC/USDT", timeframe="1h"),
            TradingPairConfig(symbol="ETH/USDT", timeframe="1h"),
        ],
        description="Trading pairs to monitor"
    )
    
    # Strategies to use
    strategies: List[StrategyConfig] = Field(
        default_factory=lambda: [
            StrategyConfig(name="cci_extreme_snapback", min_confidence=0.75),
            StrategyConfig(name="bollinger_mean_reversion", min_confidence=0.70),
            StrategyConfig(name="atr_expansion_breakout", min_confidence=0.70),
        ],
        description="Strategies to use for signal generation"
    )
    
    # Scanner settings
    scanner: ScannerConfig = Field(
        default_factory=ScannerConfig,
        description="Signal scanner configuration"
    )
    
    # Alert settings
    alerts: AlertConfig = Field(
        default_factory=AlertConfig,
        description="Alert configuration"
    )
    
    # General settings
    initial_capital: float = Field(default=10000.0, gt=0, description="Initial capital for backtesting")
    risk_per_trade: float = Field(default=0.02, ge=0.001, le=0.1, description="Risk per trade (fraction)")
    
    # Storage
    database_path: Path = Field(
        default=Path("data/signals.db"),
        description="Path to signals database"
    )
    
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "pairs": [
                    {"symbol": "BTC/USDT", "timeframe": "1h", "enabled": True},
                    {"symbol": "ETH/USDT", "timeframe": "1h", "enabled": True},
                    {"symbol": "SOL/USDT", "timeframe": "1h", "enabled": True},
                ],
                "strategies": [
                    {"name": "cci_extreme_snapback", "enabled": True, "min_confidence": 0.75},
                    {"name": "bollinger_mean_reversion", "enabled": True, "min_confidence": 0.70},
                ],
                "scanner": {
                    "scan_interval_minutes": 15,
                    "lookback_candles": 500,
                    "parallel_scanning": True
                },
                "alerts": {
                    "telegram_enabled": False,
                    "email_enabled": False
                }
            }
        }
    
    @classmethod
    def load_from_file(cls, path: Path) -> "AgentConfig":
        """Load configuration from YAML/JSON file."""
        import json
        import yaml
        
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        
        with open(path, 'r') as f:
            if path.suffix == '.json':
                data = json.load(f)
            elif path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported config format: {path.suffix}")
        
        return cls(**data)
    
    def save_to_file(self, path: Path):
        """Save configuration to YAML/JSON file."""
        import json
        import yaml
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            if path.suffix == '.json':
                json.dump(self.dict(), f, indent=2, default=str)
            elif path.suffix in ['.yaml', '.yml']:
                yaml.dump(self.dict(), f, default_flow_style=False)
            else:
                raise ValueError(f"Unsupported config format: {path.suffix}")


# Default configuration instance
default_config = AgentConfig()


if __name__ == "__main__":
    # Example: Create and save default config
    config = AgentConfig()
    config.save_to_file(Path("config/agent_config.yaml"))
    print("Default configuration saved to config/agent_config.yaml")
