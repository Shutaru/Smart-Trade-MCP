"""
Strategy Registry

Central registry for all available trading strategies.
"""

from typing import Dict, List, Optional, Type
from dataclasses import dataclass

from .base import BaseStrategy, StrategyConfig
from .rsi_strategy import RSIStrategy
from .macd_strategy import MACDStrategy
from ..core.logger import logger


@dataclass
class StrategyMetadata:
    """Metadata about a strategy."""
    
    name: str
    class_name: str
    category: str
    description: str
    required_indicators: List[str]
    default_params: Dict


class StrategyRegistry:
    """Registry for managing available trading strategies."""

    def __init__(self):
        """Initialize strategy registry."""
        self._strategies: Dict[str, Type[BaseStrategy]] = {}
        self._metadata: Dict[str, StrategyMetadata] = {}
        self._register_builtin_strategies()

    def _register_builtin_strategies(self) -> None:
        """Register all built-in strategies."""
        
        # RSI Strategy
        self.register(
            name="rsi",
            strategy_class=RSIStrategy,
            category="mean_reversion",
            description="Classic RSI oversold/overbought strategy",
            default_params={
                "rsi_period": 14,
                "oversold_level": 30,
                "overbought_level": 70,
                "exit_level": 50,
            },
        )

        # MACD Strategy
        self.register(
            name="macd",
            strategy_class=MACDStrategy,
            category="trend_following",
            description="MACD crossover trend following strategy",
            default_params={
                "fast_period": 12,
                "slow_period": 26,
                "signal_period": 9,
                "histogram_threshold": 0.0,
            },
        )
        
        # Volume Shooter Strategy
        try:
            from .volume_shooter_strategy import VolumeShooterStrategy
            
            self.register(
                name="volume_shooter",
                strategy_class=VolumeShooterStrategy,
                category="momentum",
                description="High-volume breakout with momentum confirmation",
                default_params={
                    "volume_factor": 2.0,
                    "volume_period": 50,
                    "take_profit_pct": 95.0,
                    "stop_loss_pct": 10.0,
                    "use_sar_filter": False,
                    "enable_longs": True,
                    "enable_shorts": False,
                },
            )
        except ImportError as e:
            logger.warning(f"VolumeShooterStrategy not available: {e}")
        
        # TrendFlow SuperTrend (from generated)
        try:
            from .generated.trendflow_supertrend import TrendflowSupertrend
            
            self.register(
                name="trendflow_supertrend",
                strategy_class=TrendflowSupertrend,
                category="trend_following",
                description="SuperTrend + ADX momentum with pullback entries",
                default_params={
                    "adx_threshold": 22,
                    "rsi_pullback_min": 40,
                    "rsi_pullback_max": 55,
                },
            )
        except ImportError:
            logger.warning("TrendflowSupertrend not available (implementation pending)")

        # Auto-register all 38 generated strategies
        try:
            from .generated.auto_register import register_all_generated_strategies
            register_all_generated_strategies(self)
        except Exception as e:
            logger.warning(f"Could not auto-register generated strategies: {e}")

        logger.info(f"Registered {len(self._strategies)} built-in strategies")

    def register(
        self,
        name: str,
        strategy_class: Type[BaseStrategy],
        category: str,
        description: str,
        default_params: Dict,
    ) -> None:
        """
        Register a new strategy.

        Args:
            name: Unique strategy name
            strategy_class: Strategy class (must inherit from BaseStrategy)
            category: Strategy category (e.g., 'trend_following', 'mean_reversion')
            description: Human-readable description
            default_params: Default parameter values
        """
        if not issubclass(strategy_class, BaseStrategy):
            raise ValueError(f"{strategy_class} must inherit from BaseStrategy")

        self._strategies[name] = strategy_class

        # Create temporary instance to get required indicators
        temp_instance = strategy_class()
        
        self._metadata[name] = StrategyMetadata(
            name=name,
            class_name=strategy_class.__name__,
            category=category,
            description=description,
            required_indicators=temp_instance.get_required_indicators(),
            default_params=default_params,
        )

        logger.debug(f"Registered strategy: {name} ({strategy_class.__name__})")

    def get(self, name: str, config: Optional[StrategyConfig] = None) -> BaseStrategy:
        """
        Get strategy instance by name.

        Args:
            name: Strategy name
            config: Optional strategy configuration

        Returns:
            Strategy instance

        Raises:
            KeyError: If strategy not found
        """
        if name not in self._strategies:
            raise KeyError(f"Strategy not found: {name}")

        strategy_class = self._strategies[name]
        
        # Merge default params with config
        if config is None:
            config = StrategyConfig()
        
        metadata = self._metadata[name]
        for key, value in metadata.default_params.items():
            if key not in config.params:
                config.params[key] = value

        return strategy_class(config)

    def list_strategies(
        self,
        category: Optional[str] = None,
    ) -> List[StrategyMetadata]:
        """
        List all registered strategies.

        Args:
            category: Optional category filter

        Returns:
            List of strategy metadata
        """
        strategies = list(self._metadata.values())
        
        if category:
            strategies = [s for s in strategies if s.category == category]

        return strategies

    def get_categories(self) -> List[str]:
        """
        Get all strategy categories.

        Returns:
            List of unique categories
        """
        return list(set(m.category for m in self._metadata.values()))

    def get_metadata(self, name: str) -> StrategyMetadata:
        """
        Get metadata for a strategy.

        Args:
            name: Strategy name

        Returns:
            Strategy metadata

        Raises:
            KeyError: If strategy not found
        """
        if name not in self._metadata:
            raise KeyError(f"Strategy not found: {name}")

        return self._metadata[name]


# Global registry instance
registry = StrategyRegistry()


__all__ = ["StrategyRegistry", "StrategyMetadata", "registry"]
