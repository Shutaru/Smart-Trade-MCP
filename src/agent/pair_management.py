# -*- coding: utf-8 -*-
"""
Pair Management Storage

Database for dynamic trading pair management.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

from ..core.logger import logger


class PairManagementStorage:
    """Storage for trading pair management."""
    
    def __init__(self, db_path: Path):
        """Initialize pair management storage."""
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_tables()
        logger.info(f"Pair management storage initialized: {db_path}")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _create_tables(self):
        """Create database tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Trading pairs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trading_pairs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT UNIQUE NOT NULL,
                    exchange TEXT DEFAULT 'binance',
                    enabled BOOLEAN DEFAULT 0,
                    timeframe TEXT DEFAULT '1h',
                    auto_selected BOOLEAN DEFAULT 0,
                    selection_criteria TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    enabled_at TIMESTAMP,
                    disabled_at TIMESTAMP
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_enabled ON trading_pairs(enabled)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_symbol ON trading_pairs(symbol)")
            
            # Active trades table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS active_trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    entry_time TIMESTAMP NOT NULL,
                    stop_loss REAL NOT NULL,
                    take_profit REAL NOT NULL,
                    quantity REAL NOT NULL,
                    status TEXT DEFAULT 'open',
                    exit_price REAL,
                    exit_time TIMESTAMP,
                    pnl REAL,
                    notes TEXT
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON active_trades(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trade_symbol ON active_trades(symbol)")
            
            conn.commit()
    
    # ========== PAIR MANAGEMENT ==========
    
    def add_pair(self, symbol: str, timeframe: str = "1h", 
                 enabled: bool = True, auto_selected: bool = False,
                 selection_criteria: Optional[str] = None) -> int:
        """Add a trading pair."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.now()
            enabled_at = now if enabled else None
            
            cursor.execute("""
                INSERT INTO trading_pairs 
                (symbol, timeframe, enabled, auto_selected, selection_criteria, enabled_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(symbol) DO UPDATE SET
                    timeframe = excluded.timeframe,
                    enabled = excluded.enabled,
                    auto_selected = excluded.auto_selected,
                    selection_criteria = excluded.selection_criteria,
                    enabled_at = excluded.enabled_at
            """, (symbol, timeframe, enabled, auto_selected, selection_criteria, enabled_at))
            
            conn.commit()
            return cursor.lastrowid
    
    def enable_pair(self, symbol: str):
        """Enable a trading pair."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE trading_pairs 
                SET enabled = 1, enabled_at = ?
                WHERE symbol = ?
            """, (datetime.now(), symbol))
            
            conn.commit()
            logger.info(f"? Enabled pair: {symbol}")
    
    def disable_pair(self, symbol: str):
        """
        Disable a trading pair.
        
        Note: Active trades will continue following their logic (SL/TP).
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE trading_pairs 
                SET enabled = 0, disabled_at = ?
                WHERE symbol = ?
            """, (datetime.now(), symbol))
            
            conn.commit()
            logger.info(f"? Disabled pair: {symbol}")
    
    def get_enabled_pairs(self) -> List[Dict[str, Any]]:
        """Get all enabled trading pairs."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM trading_pairs 
                WHERE enabled = 1
                ORDER BY symbol
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_pairs(self) -> List[Dict[str, Any]]:
        """Get all trading pairs."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM trading_pairs ORDER BY symbol")
            
            return [dict(row) for row in cursor.fetchall()]
    
    def bulk_enable_pairs(self, symbols: List[str]):
        """Enable multiple pairs at once."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.now()
            for symbol in symbols:
                cursor.execute("""
                    UPDATE trading_pairs 
                    SET enabled = 1, enabled_at = ?
                    WHERE symbol = ?
                """, (now, symbol))
            
            conn.commit()
            logger.info(f"? Enabled {len(symbols)} pairs")
    
    def bulk_disable_pairs(self, symbols: List[str]):
        """Disable multiple pairs at once."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.now()
            for symbol in symbols:
                cursor.execute("""
                    UPDATE trading_pairs 
                    SET enabled = 0, disabled_at = ?
                    WHERE symbol = ?
                """, (now, symbol))
            
            conn.commit()
            logger.info(f"? Disabled {len(symbols)} pairs")
    
    # ========== ACTIVE TRADES ==========
    
    def add_active_trade(self, symbol: str, strategy: str, direction: str,
                        entry_price: float, stop_loss: float, take_profit: float,
                        quantity: float) -> int:
        """Add an active trade."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO active_trades 
                (symbol, strategy, direction, entry_price, entry_time,
                 stop_loss, take_profit, quantity, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'open')
            """, (symbol, strategy, direction, entry_price, datetime.now(),
                  stop_loss, take_profit, quantity))
            
            conn.commit()
            trade_id = cursor.lastrowid
            
            logger.info(f"?? New trade opened: {symbol} {direction} @ {entry_price}")
            return trade_id
    
    def close_trade(self, trade_id: int, exit_price: float, notes: Optional[str] = None):
        """Close an active trade."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get trade details
            cursor.execute("SELECT * FROM active_trades WHERE id = ?", (trade_id,))
            trade = dict(cursor.fetchone())
            
            # Calculate PnL
            if trade['direction'] == 'long':
                pnl = (exit_price - trade['entry_price']) * trade['quantity']
            else:
                pnl = (trade['entry_price'] - exit_price) * trade['quantity']
            
            # Update trade
            cursor.execute("""
                UPDATE active_trades 
                SET status = 'closed', exit_price = ?, exit_time = ?, pnl = ?, notes = ?
                WHERE id = ?
            """, (exit_price, datetime.now(), pnl, notes, trade_id))
            
            conn.commit()
            
            logger.info(f"?? Trade closed: {trade['symbol']} PnL: {pnl:.2f}")
    
    def get_active_trades(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get active trades."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if symbol:
                cursor.execute("""
                    SELECT * FROM active_trades 
                    WHERE status = 'open' AND symbol = ?
                    ORDER BY entry_time DESC
                """, (symbol,))
            else:
                cursor.execute("""
                    SELECT * FROM active_trades 
                    WHERE status = 'open'
                    ORDER BY entry_time DESC
                """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get management statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total pairs
            cursor.execute("SELECT COUNT(*) FROM trading_pairs")
            total_pairs = cursor.fetchone()[0]
            
            # Enabled pairs
            cursor.execute("SELECT COUNT(*) FROM trading_pairs WHERE enabled = 1")
            enabled_pairs = cursor.fetchone()[0]
            
            # Active trades
            cursor.execute("SELECT COUNT(*) FROM active_trades WHERE status = 'open'")
            active_trades = cursor.fetchone()[0]
            
            # Total trades
            cursor.execute("SELECT COUNT(*) FROM active_trades")
            total_trades = cursor.fetchone()[0]
            
            return {
                'total_pairs': total_pairs,
                'enabled_pairs': enabled_pairs,
                'disabled_pairs': total_pairs - enabled_pairs,
                'active_trades': active_trades,
                'total_trades': total_trades
            }


if __name__ == "__main__":
    # Example usage
    storage = PairManagementStorage(Path("data/pair_management.db"))
    
    # Add some pairs
    storage.add_pair("BTC/USDT", enabled=True)
    storage.add_pair("ETH/USDT", enabled=True)
    storage.add_pair("SOL/USDT", enabled=False)
    
    # Get enabled
    enabled = storage.get_enabled_pairs()
    print(f"Enabled pairs: {[p['symbol'] for p in enabled]}")
    
    # Stats
    stats = storage.get_statistics()
    print(f"Stats: {stats}")
