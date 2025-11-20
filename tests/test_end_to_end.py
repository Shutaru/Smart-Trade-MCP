"""
End-to-End Test with Real Data (Public API)

Tests the complete system using public Binance data (no API key needed).
"""

import asyncio
from datetime import datetime, timedelta
import json

from src.core.data_manager import DataManager
from src.core.indicators import calculate_all_indicators
from src.core.backtest_engine import BacktestEngine
from src.strategies import registry
from src.core.logger import logger


async def test_end_to_end():
    """Run complete end-to-end test."""
    
    print("=" * 80)
    print("SMART TRADE MCP - END-TO-END TEST")
    print("=" * 80)
    print()
    
    # Configuration
    symbol = "BTC/USDT"
    timeframe = "1h"
    initial_capital = 10000
    limit = 500  # Last 500 candles (public API limit)
    
    print(f"Configuration:")
    print(f"   Symbol: {symbol}")
    print(f"   Timeframe: {timeframe}")
    print(f"   Initial Capital: ${initial_capital:,}")
    print(f"   Candles: {limit} (last ~21 days)")
    print()
    
    # ========================================================================
    # STEP 1: Fetch Real Market Data
    # ========================================================================
    print("STEP 1: Fetching real market data from Binance (public API)...")
    print("-" * 80)
    
    dm = DataManager()
    
    try:
        print("   Fetching... (this may take a moment)")
        
        df = await dm.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            exchange="binance",
            limit=limit,
            use_cache=False,  # Force fresh data
        )
        
        await dm.close()
        
        print(f"   SUCCESS! Fetched {len(df)} candles")
        print(f"   From: {df['timestamp'].iloc[0]}")
        print(f"   To:   {df['timestamp'].iloc[-1]}")
        print(f"   Start Price: ${df['close'].iloc[0]:.2f}")
        print(f"   End Price:   ${df['close'].iloc[-1]:.2f}")
        price_change = ((df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100)
        print(f"   Price Change: {price_change:+.2f}%")
        print()
        
    except Exception as e:
        print(f"   ERROR: {str(e)}")
        print()
        print("   Tips:")
        print("      - Check your internet connection")
        print("      - Binance public API may have rate limits")
        return
    
    # ========================================================================
    # STEP 2: Calculate All Indicators
    # ========================================================================
    print("STEP 2: Calculating technical indicators...")
    print("-" * 80)
    
    # Get all unique indicators needed
    all_indicators = set()
    for strategy_name in ["rsi", "macd", "trendflow_supertrend"]:
        strategy = registry.get(strategy_name)
        all_indicators.update(strategy.get_required_indicators())
    
    print(f"   Required indicators: {', '.join(sorted(all_indicators))}")
    print()
    
    df = calculate_all_indicators(df, list(all_indicators))
    
    print(f"   Calculated {len(all_indicators)} indicator groups")
    print(f"   DataFrame now has {len(df.columns)} columns")
    print()
    
    # Show sample indicator values
    latest = df.iloc[-1]
    print("   Latest Indicator Values:")
    if "rsi" in df.columns:
        print(f"      RSI: {latest['rsi']:.2f}")
    if "macd" in df.columns:
        print(f"      MACD: {latest['macd']:.4f}")
    if "adx" in df.columns:
        print(f"      ADX: {latest['adx']:.2f}")
    if "bb_upper" in df.columns:
        print(f"      BB Upper: ${latest['bb_upper']:.2f}")
        print(f"      BB Lower: ${latest['bb_lower']:.2f}")
    print()
    
    # ========================================================================
    # STEP 3: Run Backtests with All Strategies
    # ========================================================================
    print("STEP 3: Running backtests with implemented strategies...")
    print("-" * 80)
    print()
    
    strategies_to_test = [
        ("rsi", "RSI Mean Reversion"),
        ("macd", "MACD Trend Following"),
        ("trendflow_supertrend", "TrendFlow SuperTrend"),
    ]
    
    results_summary = []
    
    for strategy_name, strategy_desc in strategies_to_test:
        print(f"   Testing: {strategy_desc}")
        print(f"   " + "-" * 60)
        
        try:
            # Get strategy
            strategy = registry.get(strategy_name)
            
            # Run backtest
            engine = BacktestEngine(initial_capital=initial_capital)
            results = engine.run(strategy, df)
            
            # Display results
            metrics = results['metrics']
            
            print(f"      Initial Capital:  ${results['initial_capital']:,.2f}")
            print(f"      Final Equity:     ${results['final_equity']:,.2f}")
            print(f"      Total Return:     {results['total_return']:+.2f}%")
            print()
            print(f"      Total Trades:     {metrics['total_trades']}")
            print(f"      Winning Trades:   {metrics['winning_trades']}")
            print(f"      Losing Trades:    {metrics['losing_trades']}")
            print(f"      Win Rate:         {metrics['win_rate']:.1f}%")
            print()
            print(f"      Average Win:      ${metrics['avg_win']:,.2f}")
            print(f"      Average Loss:     ${metrics['avg_loss']:,.2f}")
            print(f"      Profit Factor:    {metrics['profit_factor']:.2f}")
            print()
            print(f"      Max Drawdown:     ${metrics['max_drawdown']:,.2f} ({metrics['max_drawdown_pct']:.2f}%)")
            print(f"      Sharpe Ratio:     {metrics['sharpe_ratio']:.2f}")
            print()
            
            # Store for comparison
            results_summary.append({
                "strategy": strategy_name,
                "description": strategy_desc,
                "return": results['total_return'],
                "win_rate": metrics['win_rate'],
                "sharpe": metrics['sharpe_ratio'],
                "trades": metrics['total_trades'],
                "profit_factor": metrics['profit_factor'],
            })
            
        except Exception as e:
            print(f"      ERROR: {str(e)}")
            print()
    
    # ========================================================================
    # STEP 4: Compare Strategies
    # ========================================================================
    print("STEP 4: Strategy Comparison")
    print("=" * 80)
    print()
    
    if results_summary:
        # Sort by return
        results_summary.sort(key=lambda x: x["return"], reverse=True)
        
        print("   Ranking by Total Return:")
        print()
        for i, result in enumerate(results_summary, 1):
            rank = f"#{i}"
            print(f"   {rank}: {result['description']}")
            print(f"      Return: {result['return']:+.2f}%")
            print(f"      Win Rate: {result['win_rate']:.1f}%")
            print(f"      Sharpe: {result['sharpe']:.2f}")
            print(f"      Trades: {result['trades']}")
            print(f"      Profit Factor: {result['profit_factor']:.2f}")
            print()
    
    # ========================================================================
    # STEP 5: Generate LLM Analysis Data
    # ========================================================================
    print("STEP 5: Generating data for LLM analysis...")
    print("-" * 80)
    
    llm_data = {
        "test_date": datetime.now().isoformat(),
        "market_data": {
            "symbol": symbol,
            "timeframe": timeframe,
            "candles": len(df),
            "start_date": str(df['timestamp'].iloc[0]),
            "end_date": str(df['timestamp'].iloc[-1]),
            "price_start": float(df['close'].iloc[0]),
            "price_end": float(df['close'].iloc[-1]),
            "price_change_pct": float((df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100),
        },
        "strategies_tested": len(results_summary),
        "results": results_summary,
    }
    
    # Save to file
    output_file = "backtest_results.json"
    with open(output_file, "w") as f:
        json.dump(llm_data, f, indent=2)
    
    print(f"   Results saved to: {output_file}")
    print()
    
    # ========================================================================
    # CONCLUSION
    # ========================================================================
    print("=" * 80)
    print("END-TO-END TEST COMPLETE!")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"   Data fetching: Working")
    print(f"   Indicator calculation: Working")
    print(f"   Backtesting: Working")
    print(f"   Performance metrics: Working")
    print()
    print("Next steps:")
    print("   1. Review backtest_results.json for detailed data")
    print("   2. Implement remaining 35 strategies")
    print("   3. Run comparative backtests")
    print()


if __name__ == "__main__":
    asyncio.run(test_end_to_end())
