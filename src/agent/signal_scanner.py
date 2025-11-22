# -*- coding: utf-8 -*-
"""
Signal Scanner

Core component for scanning multiple trading pairs and generating signals.
Supports real-time and scheduled scanning.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

from ..core.data_manager import DataManager
from ..core.logger import logger
from ..strategies import registry
from .config import AgentConfig, TradingPairConfig, StrategyConfig


class TradingSignal:
    """Represents a trading signal."""
    
    def __init__(
        self,
        symbol: str,
        strategy: str,
        direction: str,  # 'long' or 'short'
        timestamp: datetime,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        confidence: float,
        timeframe: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.symbol = symbol
        self.strategy = strategy
        self.direction = direction
        self.timestamp = timestamp
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.confidence = confidence
        self.timeframe = timeframe
        self.metadata = metadata or {}
        
        # Calculate risk/reward
        if direction == 'long':
            self.risk = entry_price - stop_loss
            self.reward = take_profit - entry_price
        else:  # short
            self.risk = stop_loss - entry_price
            self.reward = entry_price - take_profit
        
        self.risk_reward_ratio = self.reward / self.risk if self.risk > 0 else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary."""
        return {
            'symbol': self.symbol,
            'strategy': self.strategy,
            'direction': self.direction,
            'timestamp': self.timestamp.isoformat(),
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'confidence': self.confidence,
            'risk_reward_ratio': self.risk_reward_ratio,
            'timeframe': self.timeframe,
            'metadata': self.metadata
        }


class SignalScanner:
    """Autonomous signal scanner for multiple trading pairs."""
    
    def __init__(self, config: AgentConfig):
        """
        Initialize signal scanner.
        
        Args:
            config: Agent configuration
        """
        self.config = config
        self.data_manager = DataManager()
        
        logger.info("=" * 80)
        logger.info("SIGNAL SCANNER - INITIALIZED")
        logger.info("=" * 80)
        logger.info(f"Monitoring {len(config.pairs)} pairs")
        logger.info(f"Using {len(config.strategies)} strategies")
        logger.info(f"Scan interval: {config.scanner.scan_interval_minutes} minutes")
        logger.info("=" * 80)
    
    async def scan_symbol(
        self,
        pair_config: TradingPairConfig,
        strategy_config: StrategyConfig
    ) -> Optional[TradingSignal]:
        """
        Scan a single symbol with a single strategy.
        
        Args:
            pair_config: Trading pair configuration
            strategy_config: Strategy configuration
            
        Returns:
            Trading signal if found, None otherwise
        """
        try:
            # Get strategy instance
            strategy = registry.get(strategy_config.name)
            
            # Fetch latest data
            df = await self.data_manager.fetch_ohlcv(
                symbol=pair_config.symbol,
                timeframe=pair_config.timeframe,
                limit=self.config.scanner.lookback_candles
            )
            
            if df is None or len(df) < 50:
                logger.warning(
                    f"Insufficient data for {pair_config.symbol} "
                    f"({len(df) if df is not None else 0} candles)"
                )
                return None
            
            # Calculate required indicators for the strategy
            from ..core.indicators import calculate_all_indicators
            required_indicators = strategy.get_required_indicators()
            df = calculate_all_indicators(df, required_indicators)
            
            # Generate signal using strategy's backtest method
            df_with_signals = strategy.backtest_signals(df)
            
            # Check latest signal
            if len(df_with_signals) == 0:
                return None
            
            latest_row = df_with_signals.iloc[-1]
            
            # Check if signal is active (not HOLD)
            signal_value = latest_row.get('signal', 'HOLD')
            if signal_value == 'HOLD' or pd.isna(signal_value):
                return None
            
            # Get current price
            current_price = df_with_signals['close'].iloc[-1]
            
            # Determine direction from signal
            if signal_value in ['LONG', 'long']:
                direction = 'long'
            elif signal_value in ['SHORT', 'short']:
                direction = 'short'
            else:
                return None
            
            # Get stop loss and take profit if available
            stop_loss = latest_row.get('stop_loss', current_price * 0.98 if direction == 'long' else current_price * 1.02)
            take_profit = latest_row.get('take_profit', current_price * 1.05 if direction == 'long' else current_price * 0.95)
            
            # Calculate confidence (simplified - could use indicator strength)
            confidence = latest_row.get('confidence', 0.75)
            
            # Check minimum confidence
            if confidence < strategy_config.min_confidence:
                return None
            
            # Create signal
            signal = TradingSignal(
                symbol=pair_config.symbol,
                strategy=strategy_config.name,
                direction=direction,
                timestamp=datetime.now(),
                entry_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=confidence,
                timeframe=pair_config.timeframe,
                metadata={
                    'candles_analyzed': len(df),
                    'latest_close': current_price,
                }
            )
            
            logger.info(
                f"?? SIGNAL FOUND: {signal.symbol} | {signal.strategy} | "
                f"{signal.direction.upper()} @ {signal.entry_price:.2f} | "
                f"R/R: {signal.risk_reward_ratio:.2f} | "
                f"Confidence: {signal.confidence:.2%}"
            )
            
            return signal
            
        except Exception as e:
            logger.error(
                f"Error scanning {pair_config.symbol} with {strategy_config.name}: {e}",
                exc_info=True
            )
            return None
    
    async def scan_all(self) -> List[TradingSignal]:
        """
        Scan all configured pairs with all configured strategies.
        
        Returns:
            List of trading signals found
        """
        logger.info("?? Starting scan...")
        start_time = datetime.now()
        
        signals = []
        
        # Filter enabled pairs and strategies
        enabled_pairs = [p for p in self.config.pairs if p.enabled]
        enabled_strategies = [s for s in self.config.strategies if s.enabled]
        
        logger.info(f"Scanning {len(enabled_pairs)} pairs with {len(enabled_strategies)} strategies")
        
        if self.config.scanner.parallel_scanning:
            # Parallel scanning
            tasks = []
            for pair in enabled_pairs:
                for strategy in enabled_strategies:
                    tasks.append(self.scan_symbol(pair, strategy))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out None and exceptions
            signals = [
                r for r in results
                if r is not None and isinstance(r, TradingSignal)
            ]
        else:
            # Sequential scanning
            for pair in enabled_pairs:
                for strategy in enabled_strategies:
                    signal = await self.scan_symbol(pair, strategy)
                    if signal is not None:
                        signals.append(signal)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info("=" * 80)
        logger.info(f"? Scan complete!")
        logger.info(f"Found {len(signals)} signals in {elapsed:.2f} seconds")
        logger.info(f"Average: {elapsed / max(len(enabled_pairs) * len(enabled_strategies), 1):.2f}s per pair/strategy")
        logger.info("=" * 80)
        
        return signals
    
    def get_summary(self, signals: List[TradingSignal]) -> Dict[str, Any]:
        """
        Get summary of signals.
        
        Args:
            signals: List of signals
            
        Returns:
            Summary dictionary
        """
        if not signals:
            return {
                'total_signals': 0,
                'by_symbol': {},
                'by_strategy': {},
                'by_direction': {'long': 0, 'short': 0},
                'avg_confidence': 0,
                'avg_risk_reward': 0
            }
        
        by_symbol = {}
        by_strategy = {}
        by_direction = {'long': 0, 'short': 0}
        
        for signal in signals:
            # By symbol
            if signal.symbol not in by_symbol:
                by_symbol[signal.symbol] = 0
            by_symbol[signal.symbol] += 1
            
            # By strategy
            if signal.strategy not in by_strategy:
                by_strategy[signal.strategy] = 0
            by_strategy[signal.strategy] += 1
            
            # By direction
            by_direction[signal.direction] += 1
        
        avg_confidence = sum(s.confidence for s in signals) / len(signals)
        avg_risk_reward = sum(s.risk_reward_ratio for s in signals) / len(signals)
        
        return {
            'total_signals': len(signals),
            'by_symbol': by_symbol,
            'by_strategy': by_strategy,
            'by_direction': by_direction,
            'avg_confidence': avg_confidence,
            'avg_risk_reward': avg_risk_reward,
            'timestamp': datetime.now().isoformat()
        }


# Example usage
if __name__ == "__main__":
    import asyncio
    from .config import AgentConfig
    
    # Load config
    config = AgentConfig()
    
    # Create scanner
    scanner = SignalScanner(config)
    
    # Run scan
    signals = asyncio.run(scanner.scan_all())
    
    # Print summary
    summary = scanner.get_summary(signals)
    print("\n" + "=" * 80)
    print("SCAN SUMMARY")
    print("=" * 80)
    print(f"Total signals: {summary['total_signals']}")
    print(f"By symbol: {summary['by_symbol']}")
    print(f"By strategy: {summary['by_strategy']}")
    print(f"By direction: {summary['by_direction']}")
    print(f"Avg confidence: {summary['avg_confidence']:.2%}")
    print(f"Avg R/R: {summary['avg_risk_reward']:.2f}")
    print("=" * 80)
