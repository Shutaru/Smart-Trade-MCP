"""
Backtest Engine

Professional backtesting system with position tracking, risk management, and performance metrics.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

import pandas as pd
import numpy as np

from ..strategies import BaseStrategy, SignalType
from ..core.logger import logger


class PositionSide(Enum):
    """Position side enum."""
    
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass
class Position:
    """Active trading position."""
    
    side: PositionSide
    entry_price: float
    quantity: float
    entry_time: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    unrealized_pnl: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Trade:
    """Closed trade record."""
    
    side: PositionSide
    entry_price: float
    exit_price: float
    quantity: float
    entry_time: datetime
    exit_time: datetime
    pnl: float
    pnl_percent: float
    fees: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    exit_reason: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert trade to dictionary."""
        return {
            "side": self.side.value,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "quantity": self.quantity,
            "entry_time": str(self.entry_time),
            "exit_time": str(self.exit_time),
            "pnl": self.pnl,
            "pnl_percent": self.pnl_percent,
            "fees": self.fees,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "exit_reason": self.exit_reason,
            "metadata": self.metadata,
        }


class BacktestEngine:
    """
    Backtest engine for strategy validation.
    
    Simulates live trading with proper position tracking, risk management,
    and performance metrics calculation.
    """

    def __init__(
        self,
        initial_capital: float = 10000.0,
        commission_rate: float = 0.001,  # 0.1% per trade
        slippage_rate: float = 0.0005,  # 0.05% slippage
    ):
        """
        Initialize backtest engine.

        Args:
            initial_capital: Starting capital
            commission_rate: Commission as fraction (e.g., 0.001 = 0.1%)
            slippage_rate: Slippage as fraction
        """
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate

        # State
        self.cash = initial_capital
        self.equity = initial_capital
        self.position: Optional[Position] = None
        self.trades: List[Trade] = []
        self.equity_curve: List[tuple[datetime, float]] = []

        logger.info(
            f"Backtest engine initialized: capital=${initial_capital}, "
            f"commission={commission_rate*100}%, slippage={slippage_rate*100}%"
        )

    def run(
        self,
        strategy: BaseStrategy,
        df: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Run backtest on historical data.

        Args:
            strategy: Trading strategy instance
            df: DataFrame with OHLCV and indicators

        Returns:
            Dictionary with backtest results
        """
        logger.info(f"Running backtest for {strategy.name}")

        # Reset state
        self._reset()

        # Generate signals
        df_with_signals = strategy.backtest_signals(df)

        # Simulate trading
        for idx in range(len(df_with_signals)):
            row = df_with_signals.iloc[idx]
            self._process_bar(row)

        # Close any open position at end
        if self.position:
            last_row = df_with_signals.iloc[-1]
            self._close_position(
                last_row["timestamp"],
                last_row["close"],
                "end_of_data",
            )

        # Calculate metrics
        metrics = self._calculate_metrics()

        logger.info(
            f"Backtest complete: {len(self.trades)} trades, "
            f"Final equity: ${self.equity:.2f}"
        )

        return {
            "strategy": strategy.name,
            "initial_capital": self.initial_capital,
            "final_equity": self.equity,
            "total_return": (self.equity / self.initial_capital - 1) * 100,
            "total_trades": len(self.trades),
            "metrics": metrics,
            "trades": [t.to_dict() for t in self.trades],
            "equity_curve": [
                {"timestamp": str(ts), "equity": eq}
                for ts, eq in self.equity_curve
            ],
        }

    def _reset(self) -> None:
        """Reset backtest state."""
        self.cash = self.initial_capital
        self.equity = self.initial_capital
        self.position = None
        self.trades = []
        self.equity_curve = []

    def _process_bar(self, row: pd.Series) -> None:
        """
        Process a single bar (candle).

        Args:
            row: DataFrame row with OHLCV and signal data
        """
        timestamp = row["timestamp"]
        high = row["high"]
        low = row["low"]
        close = row["close"]

        # Check for stop loss / take profit hits
        if self.position:
            self._check_exits(timestamp, high, low, close)

        # Check for new signals
        signal = row.get("signal", SignalType.HOLD.value)

        if signal == SignalType.LONG.value and not self.position:
            self._open_position(
                PositionSide.LONG,
                timestamp,
                row["signal_price"],
                row.get("stop_loss"),
                row.get("take_profit"),
            )
        elif signal == SignalType.SHORT.value and not self.position:
            self._open_position(
                PositionSide.SHORT,
                timestamp,
                row["signal_price"],
                row.get("stop_loss"),
                row.get("take_profit"),
            )
        elif signal == SignalType.CLOSE_LONG.value and self.position:
            if self.position.side == PositionSide.LONG:
                self._close_position(timestamp, close, "signal_exit")
        elif signal == SignalType.CLOSE_SHORT.value and self.position:
            if self.position.side == PositionSide.SHORT:
                self._close_position(timestamp, close, "signal_exit")

        # Update equity
        self._update_equity(timestamp, close)

    def _open_position(
        self,
        side: PositionSide,
        timestamp: datetime,
        price: float,
        stop_loss: Optional[float],
        take_profit: Optional[float],
    ) -> None:
        """Open a new position."""
        # Apply slippage
        entry_price = price * (1 + self.slippage_rate) if side == PositionSide.LONG else price * (1 - self.slippage_rate)

        # Calculate position size - Use fixed percentage of initial capital
        position_value = self.initial_capital * 0.10  # 10% of capital per trade (realistic)
        quantity = position_value / entry_price

        # Calculate entry fees
        entry_fees = quantity * entry_price * self.commission_rate

        self.position = Position(
            side=side,
            entry_price=entry_price,
            quantity=quantity,
            entry_time=timestamp,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

        # Deduct position value from cash (fees will be deducted on close from P&L)
        self.cash -= position_value

        logger.debug(
            f"Opened {side.value} position: qty={quantity:.4f}, "
            f"price=${entry_price:.2f}, value=${position_value:.2f}"
        )

    def _close_position(
        self,
        timestamp: datetime,
        price: float,
        reason: str,
    ) -> None:
        """Close the current position."""
        if not self.position:
            return

        # Apply slippage
        exit_price = price * (1 - self.slippage_rate) if self.position.side == PositionSide.LONG else price * (1 + self.slippage_rate)

        # Calculate raw P&L (before fees)
        if self.position.side == PositionSide.LONG:
            raw_pnl = (exit_price - self.position.entry_price) * self.position.quantity
        else:  # SHORT
            raw_pnl = (self.position.entry_price - exit_price) * self.position.quantity

        # Calculate total fees (entry + exit)
        entry_fees = self.position.quantity * self.position.entry_price * self.commission_rate
        exit_fees = self.position.quantity * exit_price * self.commission_rate
        total_fees = entry_fees + exit_fees

        # Net P&L after fees
        net_pnl = raw_pnl - total_fees

        # Return to cash: original position value + net P&L
        position_initial_value = self.position.entry_price * self.position.quantity
        self.cash += position_initial_value + net_pnl

        # Calculate P&L percentage
        pnl_percent = (raw_pnl / position_initial_value) * 100

        # Record trade
        trade = Trade(
            side=self.position.side,
            entry_price=self.position.entry_price,
            exit_price=exit_price,
            quantity=self.position.quantity,
            entry_time=self.position.entry_time,
            exit_time=timestamp,
            pnl=net_pnl,  # Net P&L after all fees
            pnl_percent=pnl_percent,
            fees=total_fees,
            stop_loss=self.position.stop_loss,
            take_profit=self.position.take_profit,
            exit_reason=reason,
        )

        self.trades.append(trade)
        self.position = None

        logger.debug(
            f"Closed position: pnl=${net_pnl:.2f} ({pnl_percent:.2f}%), "
            f"reason={reason}"
        )

    def _check_exits(
        self,
        timestamp: datetime,
        high: float,
        low: float,
        close: float,
    ) -> None:
        """Check if stop loss or take profit was hit."""
        if not self.position:
            return

        if self.position.side == PositionSide.LONG:
            # Check stop loss
            if self.position.stop_loss and low <= self.position.stop_loss:
                self._close_position(timestamp, self.position.stop_loss, "stop_loss")
                return

            # Check take profit
            if self.position.take_profit and high >= self.position.take_profit:
                self._close_position(timestamp, self.position.take_profit, "take_profit")
                return

        else:  # SHORT
            # Check stop loss
            if self.position.stop_loss and high >= self.position.stop_loss:
                self._close_position(timestamp, self.position.stop_loss, "stop_loss")
                return

            # Check take profit
            if self.position.take_profit and low <= self.position.take_profit:
                self._close_position(timestamp, self.position.take_profit, "take_profit")
                return

    def _update_equity(self, timestamp: datetime, price: float) -> None:
        """Update equity curve."""
        equity = self.cash

        if self.position:
            if self.position.side == PositionSide.LONG:
                unrealized = (price - self.position.entry_price) * self.position.quantity
            else:  # SHORT
                unrealized = (self.position.entry_price - price) * self.position.quantity

            equity += unrealized

        self.equity = equity
        self.equity_curve.append((timestamp, equity))

    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics."""
        if not self.trades:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "profit_factor": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "max_drawdown_pct": 0.0,
            }

        # Basic stats
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl < 0]

        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0

        # Profit factor
        total_wins = sum(t.pnl for t in winning_trades)
        total_losses = abs(sum(t.pnl for t in losing_trades))
        profit_factor = total_wins / total_losses if total_losses > 0 else 0

        # Sharpe ratio (simplified - assumes daily returns)
        if len(self.equity_curve) > 1:
            equity_values = np.array([eq for _, eq in self.equity_curve])
            returns = np.diff(equity_values) / equity_values[:-1]
            sharpe = np.sqrt(365) * np.mean(returns) / (np.std(returns) + 1e-9)
        else:
            sharpe = 0.0

        # Max drawdown
        equity_values = np.array([eq for _, eq in self.equity_curve])
        running_max = np.maximum.accumulate(equity_values)
        drawdown = equity_values - running_max
        max_dd = np.min(drawdown)
        max_dd_pct = (max_dd / running_max[np.argmin(drawdown)] * 100) if len(running_max) > 0 else 0

        return {
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": win_rate * 100,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_dd,
            "max_drawdown_pct": max_dd_pct,
        }


__all__ = ["BacktestEngine", "Position", "Trade", "PositionSide"]
