# -*- coding: utf-8 -*-
"""
N-Fold Walk-Forward Analysis Test

Complete test of K-fold walk-forward validation with purging.
Demonstrates robust strategy validation and overfitting detection.
"""

# ==============================================================================
# STEP 1: FIX ENCODING (BEFORE ANY IMPORTS)
# ==============================================================================
import sys
import os

if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# ==============================================================================
# STEP 2: DISABLE ALL LOGGING GLOBALLY
# ==============================================================================
os.environ['SMART_TRADE_DISABLE_LOGGING'] = 'true'

import logging
logging.disable(logging.CRITICAL)
logging.basicConfig(level=logging.CRITICAL + 100)

from loguru import logger as loguru_logger
loguru_logger.remove()

# ==============================================================================
# NOW SAFE TO IMPORT PROJECT MODULES
# ==============================================================================
import asyncio
from pathlib import Path
import json
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from src.core.data_manager import DataManager
from src.core.indicators import calculate_all_indicators
from src.strategies import registry
from src.optimization import (
    WalkForwardAnalyzer,
    WalkForwardConfig,
    WalkForwardPresets,
    CommonParameterSpaces,
)
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live

console = Console()

print("="*80)
print("N-FOLD WALK-FORWARD ANALYSIS TEST")
print("="*80)
print()


async def main():
    """Test N-fold walk-forward analysis with RSI strategy"""
    
    # =========================================================================
    # STEP 1: FETCH DATA
    # =========================================================================
    console.print("\n[bold cyan]?? STEP 1: Fetching Historical Data[/bold cyan]\n")
    
    dm = DataManager()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 years for proper N-fold WFA
    
    df = await dm.fetch_historical(
        symbol="BTC/USDT",
        timeframe="1h",
        start_date=start_date,
        end_date=end_date,
        max_candles=10000
    )
    
    await dm.close()
    
    days = (df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).days
    console.print(f"? Fetched [green]{len(df)}[/green] candles ([yellow]{days}[/yellow] days)")
    
    # =========================================================================
    # STEP 2: PREPARE STRATEGY
    # =========================================================================
    console.print("\n[bold cyan]?? STEP 2: Loading Strategy[/bold cyan]\n")
    
    strategy_class = registry.get("rsi")
    console.print(f"? Strategy: [green]{strategy_class.name}[/green]")
    
    # Calculate indicators
    required = strategy_class.get_required_indicators()
    df = calculate_all_indicators(df, required, use_gpu=False)
    console.print(f"? Calculated [green]{len(required)}[/green] indicators")
    
    # Parameter space
    param_space = CommonParameterSpaces.rsi_strategy()
    console.print(f"? Parameter space: [green]{len(param_space)}[/green] parameters")
    
    # =========================================================================
    # STEP 3: CONFIGURE N-FOLD WFA
    # =========================================================================
    console.print("\n[bold cyan]?? STEP 3: Configuring N-Fold Walk-Forward[/bold cyan]\n")
    
    # Test different configurations
    configs = {
        "Quick (1-fold)": WalkForwardPresets.quick_validation(),
        "Standard (3-fold)": WalkForwardPresets.standard(),
        "Conservative (3-fold, strict)": WalkForwardPresets.conservative(),
    }
    
    # Let user choose or use standard (needs 2 years data!)
    selected_config = configs["Standard (3-fold)"]
    
    # Display config
    config_table = Table(title="?? Walk-Forward Configuration", show_header=True)
    config_table.add_column("Parameter", style="cyan")
    config_table.add_column("Value", style="yellow")
    
    config_table.add_row("Train Days", f"{selected_config.train_days}")
    config_table.add_row("Test Days (per fold)", f"{selected_config.test_days}")
    config_table.add_row("Step Days", f"{selected_config.step_days}")
    config_table.add_row("N Folds", f"[bold]{selected_config.n_folds}[/bold]")
    config_table.add_row("Purge Days", f"{selected_config.purge_days}")
    config_table.add_row("Min Valid Folds", f"{selected_config.min_valid_folds}/{selected_config.n_folds}")
    config_table.add_row("Min Sharpe", f"{selected_config.min_sharpe_ratio}")
    config_table.add_row("Min Win Rate", f"{selected_config.min_win_rate}%")
    config_table.add_row("Max Drawdown", f"{selected_config.max_drawdown_pct}%")
    
    console.print(config_table)
    console.print()
    
    # =========================================================================
    # STEP 4: CREATE ANALYZER
    # =========================================================================
    console.print("\n[bold cyan]?? STEP 4: Initializing Analyzer[/bold cyan]\n")
    
    analyzer = WalkForwardAnalyzer(
        df=df,
        strategy_class=strategy_class,
        param_space=param_space,
        config=selected_config,
    )
    
    console.print(f"? Analyzer ready with [green]{len(analyzer.windows)}[/green] windows")
    console.print()
    
    # Show window structure
    if len(analyzer.windows) > 0:
        window = analyzer.windows[0]
        console.print(Panel(
            f"[cyan]Example Window Structure:[/cyan]\n\n"
            f"Train: {window['train_start'].date()} to {window['train_end'].date()}\n"
            f"Folds: {len(window['folds'])} test periods\n"
            f"  - Fold 0: {window['folds'][0]['start'].date()} to {window['folds'][0]['end'].date()}\n"
            f"  - Fold 1: {window['folds'][1]['start'].date()} to {window['folds'][1]['end'].date()}\n"
            f"  - Fold 2: {window['folds'][2]['start'].date()} to {window['folds'][2]['end'].date()}\n",
            title="?? Window Example",
            style="bold blue"
        ))
        console.print()
    
    # =========================================================================
    # STEP 5: RUN ANALYSIS
    # =========================================================================
    console.print("\n[bold magenta]?? STEP 5: Running N-Fold Walk-Forward Analysis[/bold magenta]")
    console.print("[dim]This will optimize on train data and test on N out-of-sample folds...[/dim]\n")
    
    input("Press ENTER to start analysis...")
    
    console.clear()
    
    # Run analysis
    results = analyzer.analyze()
    
    # =========================================================================
    # STEP 6: DISPLAY RESULTS
    # =========================================================================
    console.clear()
    console.print("\n" + "="*80)
    console.print("[bold green]?? N-FOLD WALK-FORWARD ANALYSIS RESULTS[/bold green]")
    console.print("="*80 + "\n")
    
    # Summary table
    summary_table = Table(title="? Summary Statistics", show_header=True, header_style="bold green")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="yellow")
    
    summary = results.to_summary_dict()
    for key, value in summary.items():
        summary_table.add_row(key.replace('_', ' ').title(), str(value))
    
    console.print(summary_table)
    console.print()
    
    # Window details table
    window_table = Table(title="?? Window Details", show_header=True, header_style="bold magenta")
    window_table.add_column("Window", style="cyan")
    window_table.add_column("Train Sharpe", style="green")
    window_table.add_column("Test Sharpe", style="yellow")
    window_table.add_column("Degradation", style="red")
    window_table.add_column("Valid Folds", style="blue")
    window_table.add_column("Status", style="white")
    
    for window in results.windows:
        status = "? PASS" if window.is_valid else "? FAIL"
        degradation_str = f"{window.sharpe_degradation:+.1f}%"
        
        window_table.add_row(
            f"#{window.window_id}",
            f"{window.train_sharpe:.2f}",
            f"{window.test_sharpe:.2f}",
            degradation_str,
            f"{window.valid_folds}/{len(window.folds)}",
            status
        )
    
    console.print(window_table)
    console.print()
    
    # Fold consistency analysis
    if len(results.windows) > 0:
        console.print("\n[bold cyan]?? Fold-Level Analysis (First Window)[/bold cyan]\n")
        
        first_window = results.windows[0]
        fold_table = Table(title=f"Window {first_window.window_id} - Fold Details", show_header=True)
        fold_table.add_column("Fold", style="cyan")
        fold_table.add_column("Period", style="white")
        fold_table.add_column("Sharpe", style="green")
        fold_table.add_column("Win Rate", style="yellow")
        fold_table.add_column("Max DD", style="red")
        fold_table.add_column("Status", style="white")
        
        for fold in first_window.folds:
            period = f"{fold.start.date()} to {fold.end.date()}"
            status = "?" if fold.is_valid else "?"
            
            fold_table.add_row(
                f"Fold {fold.fold_id}",
                period,
                f"{fold.sharpe:.2f}",
                f"{fold.win_rate:.1f}%",
                f"{fold.max_dd:.1f}%",
                status
            )
        
        console.print(fold_table)
        console.print()
    
    # Final assessment
    console.print("\n[bold magenta]?? FINAL ASSESSMENT[/bold magenta]\n")
    
    assessment = Panel(
        f"[cyan]Strategy:[/cyan] {results.strategy_name}\n"
        f"[cyan]Robustness Score:[/cyan] [{'green' if results.robustness_score >= 70 else 'red'}]{results.robustness_score:.1f}/100[/]\n"
        f"[cyan]Consistency:[/cyan] {results.consistency_score:.1f}% ({results.valid_windows}/{results.total_windows} windows)\n"
        f"[cyan]Avg Test Sharpe:[/cyan] {results.avg_test_sharpe:.2f}\n"
        f"[cyan]Sharpe Degradation:[/cyan] {results.avg_sharpe_degradation:+.1f}%\n"
        f"[cyan]Is Robust?:[/cyan] [{'green' if results.is_robust else 'red'}]{'YES ?' if results.is_robust else 'NO ?'}[/]",
        title="?? Final Assessment",
        style="bold " + ("green" if results.is_robust else "red")
    )
    
    console.print(assessment)
    console.print()
    
    # =========================================================================
    # STEP 7: SAVE RESULTS
    # =========================================================================
    console.print("\n[bold cyan]?? STEP 7: Saving Results[/bold cyan]\n")
    
    results_dict = results.model_dump(mode='json')
    
    filename = f"wfa_results_{selected_config.n_folds}fold_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(results_dict, f, indent=2, default=str)
    
    console.print(f"? Results saved to: [green]{filename}[/green]")
    console.print()


if __name__ == "__main__":
    asyncio.run(main())
