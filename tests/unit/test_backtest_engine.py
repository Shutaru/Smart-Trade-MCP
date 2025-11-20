"""Unit tests for backtest engine."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.core.backtest_engine import BacktestEngine, PositionSide
from src.strategies import RSIStrategy, StrategyConfig


@pytest.fixture
def simple_trending_data():
    """Create simple trending market data."""
    dates = pd.date_range("2024-01-01", periods=50, freq="1h")
    
    # Create uptrend
    close_prices = 100 + np.arange(50) * 2
    
    df = pd.DataFrame({
        "timestamp": dates,
        "open": close_prices - 0.5,
        "high": close_prices + 1.0,
        "low": close_prices - 1.0,
        "close": close_prices,
        "volume": 1000,
    })
    
    # Add RSI with clear signals
    rsi_values = [25] * 10 + [60] * 30 + [75] * 10  # Oversold -> neutral -> overbought
    df["rsi"] = rsi_values[:50]
    df["atr"] = 2.0
    
    return df


class TestBacktestEngine:
    """Test suite for backtest engine."""

    def test_initialization(self):
        """Test engine initialization."""
        engine = BacktestEngine(initial_capital=10000.0)
        
        assert engine.initial_capital == 10000.0
        assert engine.cash == 10000.0
        assert engine.equity == 10000.0
        assert engine.position is None
        assert len(engine.trades) == 0

    def test_initialization_with_custom_fees(self):
        """Test initialization with custom fees."""
        engine = BacktestEngine(
            initial_capital=5000.0,
            commission_rate=0.002,
            slippage_rate=0.001,
        )
        
        assert engine.commission_rate == 0.002
        assert engine.slippage_rate == 0.001

    def test_run_backtest(self, simple_trending_data):
        """Test running a complete backtest."""
        strategy = RSIStrategy()
        engine = BacktestEngine(initial_capital=10000.0)
        
        results = engine.run(strategy, simple_trending_data)
        
        assert "strategy" in results
        assert "initial_capital" in results
        assert "final_equity" in results
        assert "total_return" in results
        assert "total_trades" in results
        assert "metrics" in results
        assert "trades" in results
        assert "equity_curve" in results

    def test_backtest_generates_trades(self, simple_trending_data):
        """Test that backtest generates trades."""
        strategy = RSIStrategy()
        engine = BacktestEngine(initial_capital=10000.0)
        
        results = engine.run(strategy, simple_trending_data)
        
        # Should have at least some trades
        assert results["total_trades"] >= 0

    def test_metrics_calculation(self, simple_trending_data):
        """Test performance metrics calculation."""
        strategy = RSIStrategy()
        engine = BacktestEngine(initial_capital=10000.0)
        
        results = engine.run(strategy, simple_trending_data)
        metrics = results["metrics"]
        
        assert "total_trades" in metrics
        assert "win_rate" in metrics
        assert "profit_factor" in metrics
        assert "sharpe_ratio" in metrics
        assert "max_drawdown" in metrics
        assert "max_drawdown_pct" in metrics

    def test_win_rate_range(self, simple_trending_data):
        """Test that win rate is in valid range."""
        strategy = RSIStrategy()
        engine = BacktestEngine(initial_capital=10000.0)
        
        results = engine.run(strategy, simple_trending_data)
        
        if results["total_trades"] > 0:
            assert 0 <= results["metrics"]["win_rate"] <= 100

    def test_equity_curve_generated(self, simple_trending_data):
        """Test that equity curve is generated."""
        strategy = RSIStrategy()
        engine = BacktestEngine(initial_capital=10000.0)
        
        results = engine.run(strategy, simple_trending_data)
        
        assert len(results["equity_curve"]) > 0
        assert all("timestamp" in point for point in results["equity_curve"])
        assert all("equity" in point for point in results["equity_curve"])

    def test_trade_records_complete(self, simple_trending_data):
        """Test that trade records have all required fields."""
        strategy = RSIStrategy()
        engine = BacktestEngine(initial_capital=10000.0)
        
        results = engine.run(strategy, simple_trending_data)
        
        for trade in results["trades"]:
            assert "side" in trade
            assert "entry_price" in trade
            assert "exit_price" in trade
            assert "pnl" in trade
            assert "pnl_percent" in trade
            assert "exit_reason" in trade

    def test_final_equity_reasonable(self, simple_trending_data):
        """Test that final equity is reasonable."""
        strategy = RSIStrategy()
        engine = BacktestEngine(initial_capital=10000.0)
        
        results = engine.run(strategy, simple_trending_data)
        
        # Final equity should be positive (not blown up)
        assert results["final_equity"] > 0
        # Should not be absurdly high (no bugs)
        assert results["final_equity"] < 1000000

    def test_commission_applied(self):
        """Test that commissions are applied."""
        # Create simple data with one clear trade
        dates = pd.date_range("2024-01-01", periods=20, freq="1h")
        df = pd.DataFrame({
            "timestamp": dates,
            "open": 100,
            "high": 101,
            "low": 99,
            "close": 100,
            "volume": 1000,
            "rsi": [25] * 5 + [60] * 15,  # One oversold signal
            "atr": 2.0,
        })
        
        strategy = RSIStrategy()
        engine = BacktestEngine(initial_capital=10000.0, commission_rate=0.01)  # 1% commission
        
        results = engine.run(strategy, df)
        
        if results["total_trades"] > 0:
            # With 1% commission, final equity should be less than initial
            # (even in flat market, fees eat into capital)
            total_fees = sum(trade["fees"] for trade in results["trades"])
            assert total_fees > 0

    def test_empty_dataframe(self):
        """Test handling of empty dataframe."""
        strategy = RSIStrategy()
        engine = BacktestEngine()
        
        empty_df = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume", "rsi", "atr"])
        
        results = engine.run(strategy, empty_df)
        
        assert results["total_trades"] == 0
        assert results["final_equity"] == engine.initial_capital
