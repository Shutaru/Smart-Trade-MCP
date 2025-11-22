# -*- coding: utf-8 -*-
"""
Dedicated Trading Agent

Single-purpose autonomous agent for one symbol + timeframe + strategy.
Runs independently and reports performance.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
import signal
import sys

from ..core.logger import logger
from ..core.data_manager import DataManager
from ..strategies import registry
from ..core.indicators import calculate_all_indicators
from .agent_storage import AgentStorage


class TradingAgent:
    """
    Autonomous trading agent dedicated to one symbol/strategy combination.
    
    Runs in its own process, scans continuously, generates signals,
    and executes trades (paper or live).
    """
    
    def __init__(
        self,
        agent_id: str,
        symbol: str,
        timeframe: str,
        strategy: str,
        params: Dict[str, Any],
        risk_per_trade: float = 0.02,
        scan_interval_minutes: int = 15
    ):
        """
        Initialize trading agent.
        
        Args:
            agent_id: Unique agent identifier
            symbol: Trading pair (e.g., "BTC/USDT")
            timeframe: Timeframe (e.g., "1h")
            strategy: Strategy name
            params: Strategy parameters (optimized)
            risk_per_trade: Risk per trade as fraction
            scan_interval_minutes: How often to scan
        """
        self.agent_id = agent_id
        self.symbol = symbol
        self.timeframe = timeframe
        self.strategy_name = strategy
        self.params = params
        self.risk_per_trade = risk_per_trade
        self.scan_interval_minutes = scan_interval_minutes
        
        # Initialize components
        self.data_manager = DataManager()
        self.storage = AgentStorage()
        
        # Get strategy instance
        try:
            self.strategy = registry.get(strategy)
            # Update strategy params
            if hasattr(self.strategy, 'config'):
                self.strategy.config.params.update(params)
        except Exception as e:
            logger.error(f"Failed to load strategy {strategy}: {e}")
            raise
        
        # State
        self.is_running = False
        self.current_position = None
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        logger.info("=" * 80)
        logger.info(f"AGENT {agent_id} - INITIALIZED")
        logger.info("=" * 80)
        logger.info(f"Symbol: {symbol}")
        logger.info(f"Timeframe: {timeframe}")
        logger.info(f"Strategy: {strategy}")
        logger.info(f"Scan interval: {scan_interval_minutes} min")
        logger.info("=" * 80)
    
    def run(self):
        """Main agent loop (blocking)."""
        self.is_running = True
        
        logger.info(f"?? Agent {self.agent_id} started")
        
        # Run async event loop
        asyncio.run(self._async_run())
    
    async def _async_run(self):
        """Async main loop."""
        scan_count = 0
        
        while self.is_running:
            try:
                scan_count += 1
                logger.info(f"?? Scan #{scan_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Scan for signals
                await self._scan_and_trade()
                
                # Wait for next scan
                await asyncio.sleep(self.scan_interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Agent {self.agent_id} error: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait 1 min before retry
    
    async def _scan_and_trade(self):
        """Scan for signals and execute trades."""
        try:
            # Fetch latest data
            df = await self.data_manager.fetch_ohlcv(
                symbol=self.symbol,
                timeframe=self.timeframe,
                limit=500
            )
            
            if df is None or len(df) < 50:
                logger.warning(f"Insufficient data for {self.symbol}")
                return
            
            # Calculate indicators
            required_indicators = self.strategy.get_required_indicators()
            df = calculate_all_indicators(df, required_indicators)
            
            # Generate signals
            df_with_signals = self.strategy.backtest_signals(df)
            
            # Check latest signal
            latest_row = df_with_signals.iloc[-1]
            signal_value = latest_row.get('signal', 'HOLD')
            
            if signal_value == 'HOLD' or signal_value == 0:
                logger.debug(f"No signal - {self.symbol}")
                return
            
            # Determine direction
            if signal_value in ['LONG', 'long', 1]:
                direction = 'long'
            elif signal_value in ['SHORT', 'short', -1]:
                direction = 'short'
            elif signal_value in ['CLOSE_LONG', 'CLOSE_SHORT']:
                # Exit signal
                if self.current_position:
                    await self._close_position(latest_row['close'])
                return
            else:
                return
            
            # Check if already in position
            if self.current_position:
                logger.debug(f"Already in position - {self.symbol}")
                return
            
            # Get entry/SL/TP
            entry_price = latest_row['close']
            stop_loss = latest_row.get('stop_loss', entry_price * 0.98 if direction == 'long' else entry_price * 1.02)
            take_profit = latest_row.get('take_profit', entry_price * 1.05 if direction == 'long' else entry_price * 0.95)
            
            # Calculate position size
            quantity = self._calculate_position_size(entry_price, stop_loss)
            
            # Execute trade
            await self._open_position(
                direction=direction,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                quantity=quantity
            )
            
        except Exception as e:
            logger.error(f"Error in scan_and_trade: {e}", exc_info=True)
    
    def _calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """
        Calculate position size based on risk management.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
        
        Returns:
            Position size (quantity)
        """
        # Simple fixed fractional position sizing
        # In production, this should account for account balance
        risk_amount = 1000 * self.risk_per_trade  # Assume $1000 account
        risk_per_unit = abs(entry_price - stop_loss)
        
        if risk_per_unit == 0:
            return 0.01  # Minimum size
        
        quantity = risk_amount / risk_per_unit
        
        # Round to reasonable precision
        return round(quantity, 8)
    
    async def _open_position(
        self,
        direction: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        quantity: float
    ):
        """
        Open a new position.
        
        This is paper trading implementation.
        For live trading, this would place actual orders.
        """
        logger.info("=" * 80)
        logger.info(f"?? OPENING POSITION - {self.symbol}")
        logger.info("=" * 80)
        logger.info(f"Direction: {direction.upper()}")
        logger.info(f"Entry: {entry_price:.2f}")
        logger.info(f"Stop Loss: {stop_loss:.2f}")
        logger.info(f"Take Profit: {take_profit:.2f}")
        logger.info(f"Quantity: {quantity:.8f}")
        logger.info("=" * 80)
        
        # Store position
        self.current_position = {
            "direction": direction,
            "entry_price": entry_price,
            "entry_time": datetime.now(),
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "quantity": quantity,
            "symbol": self.symbol
        }
        
        # Save to database
        self.storage.add_trade(
            agent_id=self.agent_id,
            symbol=self.symbol,
            direction=direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            quantity=quantity
        )
    
    async def _close_position(self, exit_price: float, reason: str = "Signal"):
        """
        Close current position.
        
        Args:
            exit_price: Exit price
            reason: Reason for closing
        """
        if not self.current_position:
            return
        
        # Calculate PnL
        if self.current_position["direction"] == "long":
            pnl = (exit_price - self.current_position["entry_price"]) * self.current_position["quantity"]
        else:
            pnl = (self.current_position["entry_price"] - exit_price) * self.current_position["quantity"]
        
        logger.info("=" * 80)
        logger.info(f"?? CLOSING POSITION - {self.symbol}")
        logger.info("=" * 80)
        logger.info(f"Entry: {self.current_position['entry_price']:.2f}")
        logger.info(f"Exit: {exit_price:.2f}")
        logger.info(f"PnL: {pnl:+.2f}")
        logger.info(f"Reason: {reason}")
        logger.info("=" * 80)
        
        # Update database
        self.storage.close_trade(
            agent_id=self.agent_id,
            symbol=self.symbol,
            exit_price=exit_price,
            pnl=pnl,
            notes=reason
        )
        
        # Clear position
        self.current_position = None
    
    async def _check_stop_loss_take_profit(self, current_price: float):
        """Check if SL/TP hit."""
        if not self.current_position:
            return
        
        direction = self.current_position["direction"]
        sl = self.current_position["stop_loss"]
        tp = self.current_position["take_profit"]
        
        if direction == "long":
            if current_price <= sl:
                await self._close_position(sl, "Stop Loss Hit")
            elif current_price >= tp:
                await self._close_position(tp, "Take Profit Hit")
        else:  # short
            if current_price >= sl:
                await self._close_position(sl, "Stop Loss Hit")
            elif current_price <= tp:
                await self._close_position(tp, "Take Profit Hit")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Agent {self.agent_id} received signal {signum}")
        self.stop()
        sys.exit(0)
    
    def stop(self):
        """Stop agent gracefully."""
        logger.info(f"?? Stopping agent {self.agent_id}")
        self.is_running = False
        
        # Close any open positions
        if self.current_position:
            # Get current price and close
            # (In production, fetch actual price)
            logger.warning("Agent stopped with open position!")


if __name__ == "__main__":
    # Test agent
    agent = TradingAgent(
        agent_id="test_agent_001",
        symbol="BTC/USDT",
        timeframe="1h",
        strategy="cci_extreme_snapback",
        params={},
        scan_interval_minutes=1
    )
    
    agent.run()
