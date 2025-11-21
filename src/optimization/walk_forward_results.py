# -*- coding: utf-8 -*-
"""
Walk-Forward Analysis Results

Data models for WFA results and reporting.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class WindowResult(BaseModel):
    """Results from a single walk-forward window"""
    
    window_id: int = Field(description="Window number")
    
    # Date ranges
    train_start: datetime
    train_end: datetime
    test_start: datetime
    test_end: datetime
    
    # Training metrics
    train_candles: int
    train_sharpe: float
    train_win_rate: float
    train_max_dd: float
    
    # Testing metrics (out-of-sample)
    test_candles: int
    test_sharpe: float
    test_win_rate: float
    test_max_dd: float
    test_total_return: float
    test_trades: int
    
    # Optimized parameters for this window
    best_params: Dict[str, Any]
    
    # Degradation analysis
    sharpe_degradation: float = Field(
        description="% degradation from train to test Sharpe"
    )
    win_rate_degradation: float = Field(
        description="% degradation from train to test win rate"
    )
    
    # Validation
    is_valid: bool = Field(
        description="Whether window passes validation thresholds"
    )
    
    # Performance
    optimization_time: float = Field(description="Time to optimize in seconds")
    
    def calculate_degradation(self) -> None:
        """Calculate performance degradation from train to test"""
        if self.train_sharpe != 0:
            self.sharpe_degradation = (
                (self.test_sharpe - self.train_sharpe) / abs(self.train_sharpe) * 100
            )
        else:
            self.sharpe_degradation = 0.0
        
        if self.train_win_rate != 0:
            self.win_rate_degradation = (
                (self.test_win_rate - self.train_win_rate) / self.train_win_rate * 100
            )
        else:
            self.win_rate_degradation = 0.0


class WalkForwardResults(BaseModel):
    """Complete walk-forward analysis results"""
    
    # Metadata
    strategy_name: str
    start_date: datetime
    end_date: datetime
    total_windows: int
    valid_windows: int
    
    # Window results
    windows: List[WindowResult]
    
    # Aggregate metrics (across all test periods)
    avg_test_sharpe: float
    avg_test_win_rate: float
    avg_test_max_dd: float
    avg_test_return: float
    
    # Stability metrics
    sharpe_std: float = Field(description="Standard deviation of test Sharpe ratios")
    win_rate_std: float = Field(description="Standard deviation of test win rates")
    
    # Degradation metrics
    avg_sharpe_degradation: float
    avg_win_rate_degradation: float
    
    # Consistency
    consistency_score: float = Field(
        description="% of windows that passed validation",
        ge=0.0,
        le=100.0
    )
    
    # Performance
    total_time: float
    avg_window_time: float
    
    # Overall assessment
    is_robust: bool = Field(
        description="Whether strategy is robust across all windows"
    )
    
    robustness_score: float = Field(
        description="Overall robustness score (0-100)",
        ge=0.0,
        le=100.0
    )
    
    def calculate_aggregates(self) -> None:
        """Calculate aggregate statistics from all windows"""
        import statistics
        
        if not self.windows:
            return
        
        # Filter valid windows
        valid = [w for w in self.windows if w.is_valid]
        
        if not valid:
            self.is_robust = False
            self.robustness_score = 0.0
            return
        
        # Test metrics
        test_sharpes = [w.test_sharpe for w in valid]
        test_wrs = [w.test_win_rate for w in valid]
        test_dds = [w.test_max_dd for w in valid]
        test_returns = [w.test_total_return for w in valid]
        
        self.avg_test_sharpe = statistics.mean(test_sharpes)
        self.avg_test_win_rate = statistics.mean(test_wrs)
        self.avg_test_max_dd = statistics.mean(test_dds)
        self.avg_test_return = statistics.mean(test_returns)
        
        # Stability
        self.sharpe_std = statistics.stdev(test_sharpes) if len(test_sharpes) > 1 else 0.0
        self.win_rate_std = statistics.stdev(test_wrs) if len(test_wrs) > 1 else 0.0
        
        # Degradation
        sharpe_degs = [w.sharpe_degradation for w in valid]
        wr_degs = [w.win_rate_degradation for w in valid]
        
        self.avg_sharpe_degradation = statistics.mean(sharpe_degs)
        self.avg_win_rate_degradation = statistics.mean(wr_degs)
        
        # Consistency
        self.consistency_score = (self.valid_windows / self.total_windows) * 100
        
        # Robustness assessment
        self.is_robust = (
            self.consistency_score >= 70.0 and
            self.avg_test_sharpe >= 0.5 and
            abs(self.avg_sharpe_degradation) < 30.0
        )
        
        # Robustness score (weighted combination)
        self.robustness_score = min(100.0, (
            self.consistency_score * 0.4 +
            min(100, self.avg_test_sharpe * 20) * 0.3 +
            max(0, 100 - abs(self.avg_sharpe_degradation)) * 0.3
        ))
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """Generate summary dictionary for display"""
        return {
            "strategy": self.strategy_name,
            "total_windows": self.total_windows,
            "valid_windows": self.valid_windows,
            "consistency": f"{self.consistency_score:.1f}%",
            "avg_test_sharpe": f"{self.avg_test_sharpe:.2f}",
            "avg_test_win_rate": f"{self.avg_test_win_rate:.1f}%",
            "avg_test_max_dd": f"{self.avg_test_max_dd:.1f}%",
            "sharpe_degradation": f"{self.avg_sharpe_degradation:+.1f}%",
            "robustness_score": f"{self.robustness_score:.1f}/100",
            "is_robust": "? YES" if self.is_robust else "? NO",
            "total_time": f"{self.total_time:.1f}s",
        }
