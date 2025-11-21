# -*- coding: utf-8 -*-
"""
Optimization Module

Genetic Algorithm and other optimization techniques for trading strategies.
"""

from .genetic_optimizer import GeneticOptimizer
from .parameter_space import ParameterSpace, ParameterDefinition, ParameterType, CommonParameterSpaces
from .fitness_evaluator import FitnessEvaluator, FitnessMetrics
from .config import OptimizationConfig, OptimizationPresets

__all__ = [
    "GeneticOptimizer",
    "ParameterSpace",
    "ParameterDefinition",
    "ParameterType",
    "CommonParameterSpaces",
    "FitnessEvaluator",
    "FitnessMetrics",
    "OptimizationConfig",
    "OptimizationPresets",
]
