# -*- coding: utf-8 -*-
"""
CLI Dashboard System for Smart Trade MCP

Modern, beautiful CLI dashboards using Rich library.
Replaces legacy custom print-based progress displays.

Features:
- Live updating progress bars
- GPU monitoring
- ETA calculations
- Clean, organized output
- Color-coded status
- No spam (single screen updates)
"""

from rich.console import Console
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from datetime import datetime
from typing import Dict, List, Optional
import time


# Console with Windows-compatible settings (no emoji, simple characters)
console = Console(
    emoji=False,
    legacy_windows=False,
)


class OptimizationDashboard:
    """
    Live dashboard for optimization progress.
    
    Shows:
    - Overall progress
    - Generation metrics
    - GPU utilization
    - Best fitness
    - ETA
    """
    
    def __init__(
        self,
        population_size: int,
        n_generations: int,
        n_gpus: int = 0,
        strategy_name: str = "Unknown"
    ):
        self.population_size = population_size
        self.n_generations = n_generations
        self.n_gpus = n_gpus
        self.strategy_name = strategy_name
        
        self.current_generation = 0
        self.total_evaluated = 0
        self.start_time = time.time()
        self.gen_start_time = time.time()
        
        self.best_fitness: Dict[str, float] = {}
        self.avg_fitness: Dict[str, float] = {}
        self.gpu_progress: Dict[int, tuple] = {}  # {gpu_id: (current, total)}
        
        self.gen_times: List[float] = []
        
        # Rich components
        self.layout = Layout()
        self.progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),  # Fixed width, simple ASCII bar
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console,
        )
        
        self.overall_task = self.progress.add_task(
            "[cyan]Overall Progress", total=n_generations
        )
        self.gen_task = self.progress.add_task(
            "[green]Current Generation", total=population_size
        )
    
    def _create_header(self) -> Panel:
        """Create header panel"""
        header_text = Text()
        header_text.append("?? GENETIC ALGORITHM OPTIMIZATION\n", style="bold magenta")
        header_text.append(f"Strategy: {self.strategy_name}\n", style="cyan")
        header_text.append(
            f"Population: {self.population_size} | Generations: {self.n_generations}",
            style="yellow"
        )
        
        return Panel(header_text, style="bold blue")
    
    def _create_metrics_table(self) -> Table:
        """Create metrics table"""
        table = Table(title="?? Performance Metrics", show_header=True, header_style="bold magenta")
        
        table.add_column("Metric", style="cyan")
        table.add_column("Best", style="green")
        table.add_column("Average", style="yellow")
        
        metrics = ["Sharpe Ratio", "Win Rate %", "Max Drawdown %"]
        metric_keys = ["sharpe_ratio", "win_rate", "max_drawdown"]
        
        for metric, key in zip(metrics, metric_keys):
            best_val = self.best_fitness.get(key, 0.0)
            avg_val = self.avg_fitness.get(key, 0.0)
            
            table.add_row(
                metric,
                f"{best_val:.2f}",
                f"{avg_val:.2f}"
            )
        
        return table
    
    def _create_gpu_table(self) -> Optional[Table]:
        """Create GPU utilization table"""
        if self.n_gpus == 0:
            return None
        
        table = Table(title="???  GPU Utilization", show_header=True, header_style="bold cyan")
        
        table.add_column("GPU", style="cyan")
        table.add_column("Progress", style="yellow")
        table.add_column("Status", style="green")
        
        for gpu_id in range(self.n_gpus):
            if gpu_id in self.gpu_progress:
                current, total = self.gpu_progress[gpu_id]
                pct = (current / total * 100) if total > 0 else 0
                status = "? Complete" if current >= total else "? Processing"
                table.add_row(
                    f"GPU {gpu_id}",
                    f"{current}/{total} ({pct:.0f}%)",
                    status
                )
            else:
                table.add_row(f"GPU {gpu_id}", "0/0 (0%)", "??  Idle")
        
        return table
    
    def _create_stats_panel(self) -> Panel:
        """Create statistics panel"""
        elapsed = time.time() - self.start_time
        
        stats_text = Text()
        stats_text.append(f"??  Elapsed: {self._format_time(elapsed)}\n", style="cyan")
        stats_text.append(f"?? Evaluated: {self.total_evaluated:,}\n", style="yellow")
        
        if self.gen_times:
            avg_gen_time = sum(self.gen_times) / len(self.gen_times)
            remaining = (self.n_generations - self.current_generation) * avg_gen_time
            stats_text.append(f"? ETA: {self._format_time(remaining)}\n", style="green")
            stats_text.append(f"? Speed: {self.total_evaluated/elapsed:.1f} evals/s", style="magenta")
        
        return Panel(stats_text, title="?? Statistics", style="bold blue")
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}h {minutes:02d}m {secs:02d}s"
        elif minutes > 0:
            return f"{minutes:02d}m {secs:02d}s"
        else:
            return f"{secs}s"
    
    def start(self):
        """Start the live dashboard"""
        console.clear()
        console.print(self._create_header())
        console.print()
    
    def update_generation(self, generation: int, evaluated: int):
        """Update generation progress"""
        self.current_generation = generation
        self.total_evaluated += evaluated
        
        self.progress.update(self.overall_task, completed=generation)
        self.progress.update(self.gen_task, completed=evaluated)
    
    def update_gpu(self, gpu_id: int, current: int, total: int):
        """Update GPU progress"""
        self.gpu_progress[gpu_id] = (current, total)
    
    def complete_generation(self, best_fitness: Dict[str, float], avg_fitness: Dict[str, float]):
        """Complete a generation"""
        gen_time = time.time() - self.gen_start_time
        self.gen_times.append(gen_time)
        
        self.best_fitness = best_fitness
        self.avg_fitness = avg_fitness
        
        self.gen_start_time = time.time()
    
    def render(self) -> Layout:
        """Render current dashboard state"""
        layout = Layout()
        
        layout.split_column(
            Layout(self._create_header(), size=5),
            Layout(self.progress, size=5),
            Layout(self._create_metrics_table(), size=8),
            Layout(self._create_gpu_table() if self.n_gpus > 0 else Panel("CPU Mode", style="yellow"), size=6),
            Layout(self._create_stats_panel(), size=6),
        )
        
        return layout
    
    def complete(self, final_best: Dict[str, float]):
        """Display final results"""
        console.clear()
        console.rule("[bold green]? OPTIMIZATION COMPLETE")
        
        total_time = time.time() - self.start_time
        
        # Final stats table
        table = Table(title="?? Final Results", show_header=True, header_style="bold green")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")
        
        table.add_row("Total Time", self._format_time(total_time))
        table.add_row("Total Evaluations", f"{self.total_evaluated:,}")
        table.add_row("Evaluation Speed", f"{self.total_evaluated/total_time:.1f} evals/s")
        table.add_row("Best Sharpe Ratio", f"{final_best.get('sharpe_ratio', 0):.2f}")
        table.add_row("Best Win Rate", f"{final_best.get('win_rate', 0):.1f}%")
        table.add_row("Max Drawdown", f"{final_best.get('max_drawdown', 0):.1f}%")
        
        console.print(table)
        console.print()


# Example usage
if __name__ == "__main__":
    """Demo of the optimization dashboard"""
    import random
    
    dashboard = OptimizationDashboard(
        population_size=100,
        n_generations=10,
        n_gpus=4,
        strategy_name="RSI Mean Reversion"
    )
    
    dashboard.start()
    
    with Live(dashboard.render(), console=console, refresh_per_second=10) as live:
        for gen in range(1, 11):
            dashboard.gen_start_time = time.time()
            
            # Simulate generation
            for eval_count in range(1, 101):
                dashboard.update_generation(gen, eval_count)
                
                # Simulate GPU progress
                for gpu_id in range(4):
                    gpu_current = min(eval_count // 4 + (1 if gpu_id < eval_count % 4 else 0), 25)
                    dashboard.update_gpu(gpu_id, gpu_current, 25)
                
                live.update(dashboard.render())
                time.sleep(0.05)
            
            # Complete generation
            best_fit = {
                "sharpe_ratio": 0.5 + gen * 0.15 + random.uniform(-0.1, 0.1),
                "win_rate": 50 + gen * 1.5 + random.uniform(-2, 2),
                "max_drawdown": 20 - gen * 0.5 + random.uniform(-1, 1)
            }
            
            avg_fit = {
                "sharpe_ratio": best_fit["sharpe_ratio"] * 0.7,
                "win_rate": best_fit["win_rate"] * 0.85,
                "max_drawdown": best_fit["max_drawdown"] * 1.2
            }
            
            dashboard.complete_generation(best_fit, avg_fit)
            live.update(dashboard.render())
    
    dashboard.complete(best_fit)
