# -*- coding: utf-8 -*-
"""
Optimization Module

Genetic Algorithm and Walk-Forward Analysis for trading strategies.
"""

from .genetic_optimizer import GeneticOptimizer
from .parameter_space import ParameterSpace, ParameterDefinition, ParameterType, CommonParameterSpaces
from .all_parameter_spaces import AllParameterSpaces
from .fitness_evaluator import FitnessEvaluator, FitnessMetrics
from .config import OptimizationConfig, OptimizationPresets
from .walk_forward_analyzer import WalkForwardAnalyzer
from .walk_forward_config import WalkForwardConfig, WalkForwardPresets
from .walk_forward_results import WindowResult, WalkForwardResults, FoldResult
from .walk_forward_dashboard import WalkForwardDashboard
from .ray_batch_evaluator import RayBatchEvaluator, BatchEvaluationConfig

__all__ = [
    # Genetic Optimization
    "GeneticOptimizer",
    "ParameterSpace",
    "ParameterDefinition",
    "ParameterType",
    "CommonParameterSpaces",
    "AllParameterSpaces",
    "FitnessEvaluator",
    "FitnessMetrics",
    "OptimizationConfig",
    "OptimizationPresets",
    # Walk-Forward Analysis
    "WalkForwardAnalyzer",
    "WalkForwardConfig",
    "WalkForwardPresets",
    "WindowResult",
    "WalkForwardResults",
    "FoldResult",
    "WalkForwardDashboard",
    # Ray Batch Processing
    "RayBatchEvaluator",
    "BatchEvaluationConfig",
]
