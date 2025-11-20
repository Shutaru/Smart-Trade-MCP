"""
Market Regime Detection Engine

Detects current market regime (Trending Up/Down, Ranging, Volatile, etc.)
Used for regime-aware strategy selection and live trading decisions.

Exposed via MCP for LLM access.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
import numpy as np

from .logger import logger


class MarketRegime(Enum):
    """Market regime types."""
    
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    RANGING = "RANGING"
    VOLATILE = "VOLATILE"
    CONSOLIDATING = "CONSOLIDATING"
    UNKNOWN = "UNKNOWN"


@dataclass
class RegimeAnalysis:
    """Market regime analysis result."""
    
    regime: MarketRegime
    confidence: float  # 0-1
    timestamp: datetime
    metrics: Dict[str, float]
    recommended_strategies: List[str]
    avoid_strategies: List[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "regime": self.regime.value,
            "confidence": round(self.confidence, 3),
            "timestamp": self.timestamp.isoformat(),
            "metrics": {k: round(v, 3) for k, v in self.metrics.items()},
            "recommended_strategies": self.recommended_strategies,
            "avoid_strategies": self.avoid_strategies,
            "metadata": self.metadata,
        }


class RegimeDetector:
    """
    Market Regime Detection Engine.
    
    Uses multiple technical indicators to classify market regime:
    - ADX: Trend strength
    - ATR: Volatility
    - Bollinger Band Width: Volatility/consolidation
    - EMA slopes: Trend direction
    - Price action: Higher highs/lower lows
    
    Example:
        >>> detector = RegimeDetector()
        >>> regime = detector.detect(df)
        >>> print(f"Regime: {regime.regime.value}, Confidence: {regime.confidence}")
        >>> print(f"Recommended: {regime.recommended_strategies}")
    """
    
    def __init__(
        self,
        adx_trending_threshold: float = 25.0,
        adx_strong_threshold: float = 40.0,
        atr_volatile_threshold: float = 0.03,  # 3% of price
        bb_width_consolidation: float = 1.5,   # 1.5% BB width
        bb_width_volatile: float = 4.0,        # 4% BB width
    ):
        """
        Initialize regime detector.
        
        Args:
            adx_trending_threshold: ADX above this = trending
            adx_strong_threshold: ADX above this = strong trend
            atr_volatile_threshold: ATR/price ratio for volatility
            bb_width_consolidation: BB width below this = consolidating
            bb_width_volatile: BB width above this = volatile
        """
        self.adx_trending = adx_trending_threshold
        self.adx_strong = adx_strong_threshold
        self.atr_volatile = atr_volatile_threshold
        self.bb_consolidation = bb_width_consolidation
        self.bb_volatile = bb_width_volatile
        
        logger.info("RegimeDetector initialized")
    
    def detect(
        self,
        df: pd.DataFrame,
        lookback: int = 50,
    ) -> RegimeAnalysis:
        """
        Detect current market regime.
        
        Args:
            df: DataFrame with OHLCV and indicators
            lookback: Number of candles to analyze
            
        Returns:
            RegimeAnalysis with regime classification
        """
        if len(df) < lookback:
            logger.warning(f"Insufficient data for regime detection: {len(df)} < {lookback}")
            return self._unknown_regime()
        
        # Get recent data
        recent = df.iloc[-lookback:].copy()
        current = df.iloc[-1]
        
        # Calculate metrics
        metrics = self._calculate_metrics(recent, current)
        
        # Classify regime
        regime, confidence = self._classify_regime(metrics)
        
        # Get strategy recommendations
        recommended, avoid = self._get_strategy_recommendations(regime, metrics)
        
        return RegimeAnalysis(
            regime=regime,
            confidence=confidence,
            timestamp=current.get('timestamp', datetime.now()),
            metrics=metrics,
            recommended_strategies=recommended,
            avoid_strategies=avoid,
            metadata={
                'lookback': lookback,
                'data_points': len(recent),
            }
        )
    
    def detect_historical_regimes(
        self,
        df: pd.DataFrame,
        window_size: int = 50,
    ) -> List[Tuple[datetime, datetime, MarketRegime]]:
        """
        Detect regimes across historical data.
        
        Returns list of (start_date, end_date, regime) tuples.
        Useful for regime-aware backtesting.
        
        Args:
            df: Historical data
            window_size: Rolling window for regime detection
            
        Returns:
            List of regime periods
        """
        regimes = []
        current_regime = None
        regime_start = None
        
        for i in range(window_size, len(df)):
            # Detect regime for this point
            window_df = df.iloc[i-window_size:i+1]
            analysis = self.detect(window_df, lookback=window_size)
            
            timestamp = df.iloc[i]['timestamp']
            
            # Check if regime changed
            if analysis.regime != current_regime:
                # Save previous regime period
                if current_regime is not None:
                    regimes.append((regime_start, timestamp, current_regime))
                
                # Start new regime
                current_regime = analysis.regime
                regime_start = timestamp
        
        # Add final regime
        if current_regime is not None:
            regimes.append((regime_start, df.iloc[-1]['timestamp'], current_regime))
        
        logger.info(f"Detected {len(regimes)} regime periods in historical data")
        return regimes
    
    def _calculate_metrics(
        self,
        df: pd.DataFrame,
        current: pd.Series,
    ) -> Dict[str, float]:
        """Calculate regime detection metrics."""
        
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        
        # ADX - Trend strength
        adx = current.get('adx', 0)
        
        # ATR - Volatility
        atr = current.get('atr', 0)
        atr_pct = (atr / current['close']) * 100 if current['close'] > 0 else 0
        
        # Bollinger Band Width - Volatility/consolidation
        bb_upper = current.get('bb_upper', current['close'])
        bb_lower = current.get('bb_lower', current['close'])
        bb_middle = current.get('bb_middle', current['close'])
        bb_width = ((bb_upper - bb_lower) / bb_middle) * 100 if bb_middle > 0 else 0
        
        # EMA slopes - Trend direction
        ema_12 = current.get('ema_12', current['close'])
        ema_26 = current.get('ema_26', current['close'])
        ema_50 = current.get('ema_50', current['close'])
        ema_200 = current.get('ema_200', current['close'])
        
        # Calculate EMA alignment (bullish or bearish)
        ema_bullish = (ema_12 > ema_26 > ema_50 > ema_200)
        ema_bearish = (ema_12 < ema_26 < ema_50 < ema_200)
        
        # Price action - Higher highs / lower lows
        hh_count = sum(1 for i in range(1, len(high)) if high[i] > high[i-1])
        ll_count = sum(1 for i in range(1, len(low)) if low[i] < low[i-1])
        
        hh_ratio = hh_count / (len(high) - 1) if len(high) > 1 else 0
        ll_ratio = ll_count / (len(low) - 1) if len(low) > 1 else 0
        
        # Price vs EMAs
        price_above_ema12 = current['close'] > ema_12
        price_above_ema200 = current['close'] > ema_200
        
        # Volatility metrics
        returns = np.diff(close) / close[:-1]
        volatility = np.std(returns) * 100 if len(returns) > 0 else 0
        
        return {
            'adx': adx,
            'atr_pct': atr_pct,
            'bb_width': bb_width,
            'volatility': volatility,
            'ema_bullish': 1.0 if ema_bullish else 0.0,
            'ema_bearish': 1.0 if ema_bearish else 0.0,
            'hh_ratio': hh_ratio,
            'll_ratio': ll_ratio,
            'price_above_ema12': 1.0 if price_above_ema12 else 0.0,
            'price_above_ema200': 1.0 if price_above_ema200 else 0.0,
        }
    
    def _classify_regime(
        self,
        metrics: Dict[str, float],
    ) -> Tuple[MarketRegime, float]:
        """
        Classify regime based on metrics.
        
        Returns (regime, confidence).
        """
        adx = metrics['adx']
        atr_pct = metrics['atr_pct']
        bb_width = metrics['bb_width']
        volatility = metrics['volatility']
        ema_bullish = metrics['ema_bullish']
        ema_bearish = metrics['ema_bearish']
        hh_ratio = metrics['hh_ratio']
        ll_ratio = metrics['ll_ratio']
        price_above_ema200 = metrics['price_above_ema200']
        
        # VOLATILE - High ATR and BB width
        if atr_pct > self.atr_volatile or bb_width > self.bb_volatile:
            confidence = min(
                (atr_pct / self.atr_volatile + bb_width / self.bb_volatile) / 2,
                1.0
            )
            return MarketRegime.VOLATILE, confidence
        
        # CONSOLIDATING - Low volatility, tight BB
        if bb_width < self.bb_consolidation and volatility < 2.0:
            confidence = 1.0 - (bb_width / self.bb_consolidation)
            return MarketRegime.CONSOLIDATING, confidence
        
        # TRENDING UP - Strong ADX + bullish EMAs + higher highs
        if (adx > self.adx_trending and 
            ema_bullish > 0.5 and 
            hh_ratio > 0.6 and
            price_above_ema200 > 0.5):
            
            confidence = min(
                (adx / self.adx_strong + ema_bullish + hh_ratio) / 3,
                1.0
            )
            return MarketRegime.TRENDING_UP, confidence
        
        # TRENDING DOWN - Strong ADX + bearish EMAs + lower lows
        if (adx > self.adx_trending and 
            ema_bearish > 0.5 and 
            ll_ratio > 0.6 and
            price_above_ema200 < 0.5):
            
            confidence = min(
                (adx / self.adx_strong + ema_bearish + ll_ratio) / 3,
                1.0
            )
            return MarketRegime.TRENDING_DOWN, confidence
        
        # RANGING - Low ADX, no clear trend
        if adx < self.adx_trending:
            confidence = 1.0 - (adx / self.adx_trending)
            return MarketRegime.RANGING, confidence
        
        # Default: UNKNOWN
        return MarketRegime.UNKNOWN, 0.0
    
    def _get_strategy_recommendations(
        self,
        regime: MarketRegime,
        metrics: Dict[str, float],
    ) -> Tuple[List[str], List[str]]:
        """
        Get strategy recommendations based on regime.
        
        Returns (recommended_strategies, avoid_strategies).
        """
        recommendations = {
            MarketRegime.TRENDING_UP: {
                'recommended': [
                    'ema_stack_momentum',
                    'supertrend_flip',
                    'trendflow_supertrend',
                    'breakout strategies',
                    'donchian_volatility_breakout',
                    'ema_stack_regime_flip',
                ],
                'avoid': [
                    'bollinger_mean_reversion',
                    'cci_extreme_snapback',
                    'rsi_oversold_bounce',
                    'mean reversion strategies',
                ],
            },
            MarketRegime.TRENDING_DOWN: {
                'recommended': [
                    'supertrend_flip (short)',
                    'ema_stack_momentum (short)',
                    'breakdown strategies',
                ],
                'avoid': [
                    'bollinger_mean_reversion (long)',
                    'rsi_oversold_bounce',
                    'long-only strategies',
                ],
            },
            MarketRegime.RANGING: {
                'recommended': [
                    'bollinger_mean_reversion',
                    'cci_extreme_snapback',
                    'rsi_oversold_bounce',
                    'vwap_mean_reversion',
                    'keltner_pullback_continuation',
                ],
                'avoid': [
                    'breakout strategies',
                    'trend following',
                    'momentum strategies',
                ],
            },
            MarketRegime.VOLATILE: {
                'recommended': [
                    'atr_expansion_breakout',
                    'bollinger_squeeze_breakout',
                    'keltner_expansion',
                    'volatility_weighted_breakout',
                ],
                'avoid': [
                    'tight stop-loss strategies',
                    'scalping strategies',
                ],
            },
            MarketRegime.CONSOLIDATING: {
                'recommended': [
                    'bollinger_squeeze_breakout',
                    'range breakout strategies',
                    'wait for expansion',
                ],
                'avoid': [
                    'all strategies (wait for volatility)',
                ],
            },
            MarketRegime.UNKNOWN: {
                'recommended': [],
                'avoid': ['all strategies (unclear regime)'],
            },
        }
        
        config = recommendations.get(regime, {'recommended': [], 'avoid': []})
        return config['recommended'], config['avoid']
    
    def _unknown_regime(self) -> RegimeAnalysis:
        """Return unknown regime analysis."""
        return RegimeAnalysis(
            regime=MarketRegime.UNKNOWN,
            confidence=0.0,
            timestamp=datetime.now(),
            metrics={},
            recommended_strategies=[],
            avoid_strategies=['all (insufficient data)'],
            metadata={'error': 'Insufficient data'},
        )


# Global detector instance
_detector = None


def get_regime_detector() -> RegimeDetector:
    """Get global regime detector instance."""
    global _detector
    if _detector is None:
        _detector = RegimeDetector()
    return _detector


__all__ = [
    'MarketRegime',
    'RegimeAnalysis',
    'RegimeDetector',
    'get_regime_detector',
]
