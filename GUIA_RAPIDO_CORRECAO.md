# ?? GUIA RÁPIDO - CORREÇÃO DE ESTRATÉGIAS

## ? USO IMEDIATO

### 1?? Ver Mudanças Propostas (Seguro)

```bash
python scripts/auto_fix_strategies.py --preview
```

**Output:**
```
==============================================================================
PREVIEW MODE - No changes will be applied
==============================================================================

?? Processing 38 strategies...

==============================================================================
STRATEGY: bollinger_mean_reversion
==============================================================================

?? OLD (CURRENT):
------------------------------------------------------------------------------
  -     def __init__(self, config: StrategyConfig = None):
  -         super().__init__(config)
  -         self.config.stop_loss_atr_mult = 0.8
  -         self.config.take_profit_rr_ratio = 2.0

?? NEW (PROPOSED):
------------------------------------------------------------------------------
  +     def __init__(self, config: StrategyConfig = None):
  +         """Initialize BollingerMeanReversion strategy."""
  +         super().__init__(config)
  +         
  +         # ? OPTIMIZABLE PARAMETERS (auto-generated)
  +         self.bb_period = self.config.get("bb_period", 20)
  +         self.bb_std = self.config.get("bb_std", 2.0)
  +         self.rsi_filter = self.config.get("rsi_filter", 50)
  +         self.sl_atr_mult = self.config.get("sl_atr_mult", 2.0)
  +         self.tp_rr_mult = self.config.get("tp_rr_mult", 2.0)

==============================================================================
???  bollinger_mean_reversion: PREVIEW ONLY (use --apply to save)
```

### 2?? Corrigir UMA Estratégia (Teste)

```bash
python scripts/auto_fix_strategies.py --strategy bollinger_mean_reversion --apply
```

### 3?? Corrigir TODAS as Estratégias (Depois de revisar)

```bash
python scripts/auto_fix_strategies.py --apply
```

---

## ?? VERIFICAÇÃO

### Teste se Funcionou

```python
from src.strategies.generated.bollinger_mean_reversion import BollingerMeanReversion
from src.strategies.base import StrategyConfig

# Test 1: Parâmetros conectados?
config = StrategyConfig(params={"bb_period": 25, "bb_std": 2.5})
strategy = BollingerMeanReversion(config)

print(f"bb_period: {strategy.bb_period}")  # Deve ser 25
print(f"bb_std: {strategy.bb_std}")        # Deve ser 2.5

# Test 2: Otimização funciona?
from src.optimization import GeneticOptimizer, AllParameterSpaces
from src.optimization.config import OptimizationConfig

optimizer = GeneticOptimizer(
    df=df,  # Your OHLCV data
    strategy_class=BollingerMeanReversion,
    param_space=AllParameterSpaces.bollinger_mean_reversion_strategy(),
    config=OptimizationConfig(population_size=10, n_generations=2),
    use_smart_ranges=True  # Meta-Learner ativo!
)

results = optimizer.optimize()
print(results["best_params"])
```

---

## ?? WORKFLOW RECOMENDADO

### Fase 1: Preview & Review (15 min)

```bash
# Ver todas as mudanças
python scripts/auto_fix_strategies.py --preview > changes_preview.txt

# Revisar ficheiro gerado
# Verificar se mudanças fazem sentido
```

### Fase 2: Teste Unitário (30 min)

```bash
# Corrigir 1 estratégia de cada categoria
python scripts/auto_fix_strategies.py --strategy bollinger_mean_reversion --apply
python scripts/auto_fix_strategies.py --strategy trendflow_supertrend --apply
python scripts/auto_fix_strategies.py --strategy ema_stack_momentum --apply

# Testar cada uma
python test_fixed_strategies.py
```

### Fase 3: Correção em Massa (5 min)

```bash
# Se testes OK, corrigir tudo
python scripts/auto_fix_strategies.py --apply
```

### Fase 4: Verificação Final (20 min)

```bash
# Testar build
python -m pytest tests/

# Testar otimização com várias estratégias
python test_optimization_all.py
```

---

## ?? NOTAS IMPORTANTES

### O Script FAZ:
? Gera `__init__` correto com base em `default_params`  
? Conecta TODOS os parâmetros ao `config`  
? Adiciona docstring  
? Preserva resto do código  

### O Script NÃO FAZ:
? Alterar `generate_signals()` - Tens de fazer manualmente!  
? Adicionar validação de parâmetros  
? Otimizar lógica da estratégia  

### Depois de Corrigir __init__, Tens de:
1. Abrir `generate_signals()` manualmente
2. Substituir valores hardcoded por `self.param_name`
3. Exemplo:
   ```python
   # ? ANTES
   bb_std = 2.0
   
   # ? DEPOIS
   bb_std = self.bb_std
   ```

---

## ?? EXEMPLO COMPLETO

### Estratégia: `bollinger_mean_reversion.py`

#### ? PASSO 1: Corrigir __init__ (Automático)

```bash
python scripts/auto_fix_strategies.py --strategy bollinger_mean_reversion --apply
```

#### ? PASSO 2: Corrigir generate_signals (Manual)

Abrir `src/strategies/generated/bollinger_mean_reversion.py`:

```python
def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
    signals, pos = [], None
    for i in range(1, len(df)):
        r = df.iloc[i]
        close = r["close"]
        
        # ? ANTES (hardcoded)
        bb_lower = r.get("bb_lower", close * 0.98)
        bb_std = 2.0
        
        # ? DEPOIS (usando self.bb_std)
        bb_lower = r.get("bb_lower", close * 0.98)
        bb_std = self.bb_std  # ? Agora otimizável!
        
        # Rest of logic...
```

#### ? PASSO 3: Testar

```python
from src.strategies.generated.bollinger_mean_reversion import BollingerMeanReversion
from src.strategies.base import StrategyConfig

config = StrategyConfig(params={"bb_std": 2.5})
strategy = BollingerMeanReversion(config)

assert strategy.bb_std == 2.5  # ? Deve passar
```

---

## ?? CHECKLIST

### Para CADA Estratégia:

- [ ] Run `auto_fix_strategies.py --strategy XXX --apply`
- [ ] Abrir ficheiro `.py`
- [ ] Procurar por valores hardcoded em `generate_signals()`
- [ ] Substituir por `self.param_name`
- [ ] Testar com `assert strategy.param_name == expected_value`
- [ ] Testar otimização com `GeneticOptimizer`
- [ ] Verificar logs do Meta-Learner: `?? Meta-Learner ENABLED`

### Estratégias Prioritárias:

1. [ ] `bollinger_mean_reversion` (win rate 60-70%)
2. [ ] `trendflow_supertrend` (Sharpe 2.0+)
3. [ ] `ema_cloud_trend` (pullback master)
4. [ ] `triple_momentum_confluence` (high confidence)
5. [ ] `rsi_band_reversion` (classic)

---

## ?? TROUBLESHOOTING

### Problema: Script não encontra __init__
**Solução:** Verificar se estratégia tem `def __init__` definido.

### Problema: Parâmetros não conectam
**Solução:** Verificar se parâmetro está em `default_params` no metadata.

### Problema: Otimização não usa novos valores
**Solução:** 
1. Verificar se `generate_signals()` usa `self.param_name`
2. Verificar se `AllParameterSpaces` tem entrada para estratégia
3. Verificar logs: Deve aparecer `?? Meta-Learner ENABLED`

### Problema: Estratégia não aparece no registry
**Solução:**
```python
from src.strategies import registry
print(registry.list_strategies())  # Ver todas disponíveis
```

---

## ?? QUANDO TERMINAR

### Validação Final:

```python
# Test 1: Todas as estratégias registadas?
from src.strategies import registry
strategies = registry.list_strategies()
print(f"Total strategies: {len(strategies)}")  # Deve ser 41

# Test 2: Todas otimizáveis?
from src.optimization import AllParameterSpaces
for strategy in strategies:
    method = getattr(AllParameterSpaces, f"{strategy.name}_strategy", None)
    assert method is not None, f"{strategy.name} sem parameter space!"

# Test 3: Meta-Learner funciona?
from src.optimization.meta_learner import ParameterMetaLearner
learner = ParameterMetaLearner()
for strategy in strategies:
    ranges = learner.get_naive_ranges(strategy.name)
    assert len(ranges) > 0, f"{strategy.name} sem NAIVE ranges!"

print("? TUDO OK! Sistema pronto para produção!")
```

---

**PRONTO! Segue estes passos e todas as 41 estratégias estarão corrigidas e otimizáveis! ??**
