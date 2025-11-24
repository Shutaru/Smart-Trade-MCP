# -*- coding: utf-8 -*-
"""
PLANO DE CORREÇÃO: SMART-TRADE MCP v2

PROBLEMA IDENTIFICADO:
=====================
1. ? Parâmetros definidos em `default_params` mas NÃO usados nos __init__
2. ? Parameter spaces definidos mas sem conexão às estratégias
3. ? Meta-Learner não implementado (ranges sempre NAIVE)

SOLUÇÃO IMPLEMENTADA:
====================

? 1. META-LEARNER (src/optimization/meta_learner.py)
   - Analisa regime de mercado (TRENDING, RANGING, VOLATILE)
   - Adapta ranges de parâmetros baseado no regime
   - Reduz espaço de busca em 50-90%
   - Importado do Smart-Trade v1

? 2. GENETIC OPTIMIZER INTEGRATION (src/optimization/genetic_optimizer.py)
   - Usa Meta-Learner por padrão (use_smart_ranges=True)
   - Aplica SMART ranges automaticamente
   - Logs indicam se está usando SMART ou NAIVE

? 3. EXEMPLO: atr_expansion_breakout.py (JÁ CORRIGIDA)
   ```python
   def __init__(self, config: StrategyConfig = None):
       super().__init__(config)
       
       # ? PARAMETROS CONECTADOS
       self.atr_period = self.config.get("atr_period", 14)
       self.atr_multiplier = self.config.get("atr_multiplier", 1.25)
       self.config.stop_loss_atr_mult = self.config.get("stop_loss_atr_mult", 2.2)
       self.config.take_profit_rr_ratio = self.config.get("take_profit_rr_ratio", 2.4)
   
   def generate_signals(self, df):
       # ? USA self.atr_period em vez de hardcoded 14
       atr_avg = df["atr"].rolling(self.atr_period).mean()
       
       # ? USA self.atr_multiplier
       atr_expanding = atr > atr_avg * self.atr_multiplier
   ```

ESTRATÉGIAS QUE PRECISAM CORREÇÃO:
==================================

?? **MEAN REVERSION (5 strategies)**
   - bollinger_mean_reversion.py ? (hardcoded values)
   - rsi_band_reversion.py ?
   - ema200_tap_reversion.py ?
   - vwap_mean_reversion.py ?

?? **TREND FOLLOWING (5 strategies)**
   - trendflow_supertrend.py ?
   - ema_cloud_trend.py ?
   - macd_zero_trend.py ?
   - adx_trend_filter_plus.py ?

?? **BREAKOUT (7 strategies)**
   - bollinger_squeeze_breakout.py ?
   - keltner_expansion.py ?
   - donchian_volatility_breakout.py ?
   - channel_squeeze_plus.py ?
   - volatility_weighted_breakout.py ?
   - london_breakout_atr.py ?
   - vwap_breakout.py ?
   - atr_expansion_breakout.py ? (CORRIGIDA!)

?? **MOMENTUM (8 strategies)**
   - ema_stack_momentum.py ?
   - mfi_impulse_momentum.py ?
   - triple_momentum_confluence.py ?
   - multi_oscillator_confluence.py ?
   - obv_trend_confirmation.py ?
   - trend_volume_combo.py ?
   - ema_stack_regime_flip.py ?

?? **HYBRID (6 strategies)**
   - vwap_institutional_trend.py ?
   - regime_adaptive_core.py ?

TEMPLATE DE CORREÇÃO:
====================

Para CADA estratégia, seguir este template:

```python
def __init__(self, config: StrategyConfig = None):
    super().__init__(config)
    
    # ? CONNECT ALL PARAMETERS from metadata
    self.param1 = self.config.get("param1", DEFAULT_VALUE)
    self.param2 = self.config.get("param2", DEFAULT_VALUE)
    # ... etc for ALL parameters in default_params
    
    # ? CONNECT RISK MANAGEMENT
    self.config.stop_loss_atr_mult = self.config.get("stop_loss_atr_mult", 2.0)
    self.config.take_profit_rr_ratio = self.config.get("take_profit_rr_ratio", 2.5)

def generate_signals(self, df):
    # ? USE self.param1 instead of hardcoded values
    # ? USE self.param2 instead of hardcoded values
    # ... etc
```

PRIORIDADE DE CORREÇÃO:
======================

?? ALTA (estratégias mais usadas):
   1. bollinger_mean_reversion.py
   2. trendflow_supertrend.py
   3. ema_cloud_trend.py
   4. triple_momentum_confluence.py

?? MÉDIA (úteis mas menos críticas):
   5. rsi_band_reversion.py
   6. macd_zero_trend.py
   7. bollinger_squeeze_breakout.py

?? BAIXA (nice-to-have):
   - Resto das estratégias

TESTING WORKFLOW:
================

Após correção de CADA estratégia:

1. Verificar imports:
   ```python
   from src.strategies.generated.strategy_name import StrategyName
   strategy = StrategyName()
   ```

2. Verificar parâmetros conectados:
   ```python
   config = StrategyConfig(params={"param1": 20})
   strategy = StrategyName(config)
   assert strategy.param1 == 20  # ? Deve passar
   ```

3. Testar optimização:
   ```python
   from src.optimization import GeneticOptimizer
   optimizer = GeneticOptimizer(
       df=df,
       strategy_class=StrategyName,
       param_space=AllParameterSpaces.strategy_name_strategy(),
       config=OptimizationConfig(population_size=10, n_generations=2)
   )
   results = optimizer.optimize()
   ```

4. Verificar Meta-Learner:
   ```
   ?? Meta-Learner ENABLED - Using SMART parameter ranges
   ? Applied SMART ranges: X parameters adapted to market regime
   ```

PRÓXIMOS PASSOS:
===============

1. ? Meta-Learner implementado
2. ? GeneticOptimizer integrado
3. ? Exemplo (atr_expansion_breakout) corrigido
4. ? Corrigir 40 estratégias restantes (usar template acima)
5. ? Testar cada uma com optimization
6. ? Deploy bots com parâmetros otimizados

TEMPO ESTIMADO:
==============

- Meta-Learner: ? DONE (2h)
- Optimizer Integration: ? DONE (1h)
- Fix 40 strategies: ? TODO (~4-6h usando script automatizado)
- Testing: ? TODO (~2h)

TOTAL: ~8-10h de trabalho restante

AUTOMATION SCRIPT:
==================

Para acelerar, pode-se criar script que:
1. Lê metadata de cada estratégia
2. Extrai default_params
3. Gera __init__ correto automaticamente
4. Substitui no ficheiro

Mas requer cuidado para não quebrar lógica existente!

STATUS ATUAL:
============

? INFRASTRUCTURE READY
   - Meta-Learner: 100%
   - Optimizer Integration: 100%
   - Parameter Spaces: 100%

? STRATEGIES CONNECTION: 2.5% (1/40)
   - atr_expansion_breakout: ?
   - Remaining 39: ?

?? OBJETIVO: 100% strategies connected + tested
"""

print(__doc__)
