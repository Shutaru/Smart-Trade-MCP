"""
Example: Run a Simple Backtest

This script demonstrates how to:
1. Fetch market data
2. Calculate indicators
3. Run a strategy backtest
4. Display results
"""

import asyncio
from datetime import datetime, timedelta

from src.core.data_manager import DataManager
from src.core.indicators import calculate_all_indicators
from src.core.backtest_engine import BacktestEngine
from src.strategies import registry
from src.core.logger import logger


async def main():
    """Run a simple backtest example."""
    
    print("=" * 60)
    print("?? Smart Trade MCP - Backtest Example")
    print("=" * 60)
    print()
    
    # Configuration
    symbol = "BTC/USDT"
    timeframe = "1h"
    strategy_name = "rsi"
    initial_capital = 10000
    
    print(f"?? Symbol: {symbol}")
    print(f"? Timeframe: {timeframe}")
    print(f"?? Strategy: {strategy_name}")
    print(f"?? Initial Capital: ${initial_capital}")
    print()
    
    # Step 1: Fetch market data
    print("?? Fetching market data...")
    dm = DataManager()
    
    try:
        # Fetch last 30 days of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        df = await dm.fetch_historical(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
        )
        
        await dm.close()
        
        print(f"? Fetched {len(df)} candles")
        print(f"   From: {df['timestamp'].iloc[0]}")
        print(f"   To:   {df['timestamp'].iloc[-1]}")
        print()
        
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        print(f"? Error: {e}")
        print("?? Tip: Make sure you have internet connection and CCXT is installed")
        return
    
    # Step 2: Get strategy and calculate indicators
    print(f"?? Preparing strategy: {strategy_name}")
    strategy = registry.get(strategy_name)
    
    required_indicators = strategy.get_required_indicators()
    print(f"   Required indicators: {', '.join(required_indicators)}")
    
    df = calculate_all_indicators(df, required_indicators)
    print(f"? Indicators calculated")
    print()
    
    # Step 3: Run backtest
    print("?? Running backtest...")
    engine = BacktestEngine(initial_capital=initial_capital)
    results = engine.run(strategy, df)
    
    print("? Backtest complete!")
    print()
    
    # Step 4: Display results
    print("=" * 60)
    print("?? BACKTEST RESULTS")
    print("=" * 60)
    print()
    
    print(f"?? Initial Capital:  ${results['initial_capital']:,.2f}")
    print(f"?? Final Equity:     ${results['final_equity']:,.2f}")
    print(f"?? Total Return:     {results['total_return']:+.2f}%")
    print()
    
    metrics = results['metrics']
    print(f"?? Total Trades:     {metrics['total_trades']}")
    print(f"? Winning Trades:   {metrics['winning_trades']}")
    print(f"? Losing Trades:    {metrics['losing_trades']}")
    print(f"?? Win Rate:         {metrics['win_rate']:.1f}%")
    print()
    
    print(f"?? Average Win:      ${metrics['avg_win']:,.2f}")
    print(f"??  Average Loss:     ${metrics['avg_loss']:,.2f}")
    print(f"??  Profit Factor:    {metrics['profit_factor']:.2f}")
    print()
    
    print(f"?? Max Drawdown:     ${metrics['max_drawdown']:,.2f} ({metrics['max_drawdown_pct']:.2f}%)")
    print(f"?? Sharpe Ratio:     {metrics['sharpe_ratio']:.2f}")
    print()
    
    # Show recent trades
    if results['trades']:
        print("=" * 60)
        print("?? RECENT TRADES (Last 5)")
        print("=" * 60)
        print()
        
        for i, trade in enumerate(results['trades'][-5:], 1):
            profit_emoji = "??" if trade['pnl'] > 0 else "??"
            print(f"{profit_emoji} Trade #{i}:")
            print(f"   Side:        {trade['side']}")
            print(f"   Entry:       ${trade['entry_price']:.2f}")
            print(f"   Exit:        ${trade['exit_price']:.2f}")
            print(f"   P&L:         ${trade['pnl']:+,.2f} ({trade['pnl_percent']:+.2f}%)")
            print(f"   Exit Reason: {trade['exit_reason']}")
            print()
    
    print("=" * 60)
    print("? Done! Check the results above.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
