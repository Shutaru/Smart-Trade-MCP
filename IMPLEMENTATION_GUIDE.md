# ?? Guia de Implementação das 38 Estratégias

**Status Atual:** 14 Indicadores ? | 38 Estruturas ? | 3 Implementadas ?  
**Próximo Passo:** Implementar as restantes 35 estratégias

---

## ? PROGRESSO ATUAL

### Indicadores Implementados (14/14) - 100% ?
- ? EMA, SMA, RMA
- ? RSI
- ? MACD
- ? Bollinger Bands
- ? ATR
- ? ADX
- ? **CCI** (novo)
- ? **Donchian Channels** (novo)
- ? **Keltner Channels** (novo)
- ? **MFI** (novo)
- ? **OBV** (novo)
- ? **Stochastic** (novo)
- ? **SuperTrend** (novo)
- ? **VWAP** (novo)

### Estratégias Implementadas (3/38) - 8%
- ? `rsi` - RSI Strategy
- ? `macd` - MACD Strategy  
- ? `trendflow_supertrend` - TrendFlow SuperTrend

### Estruturas Criadas (38/38) - 100% ?
Todas as 38 estratégias têm ficheiros placeholder em `src/strategies/generated/`

---

## ?? PADRÃO DE IMPLEMENTAÇÃO

Cada estratégia segue este padrão do repo antigo:

```python
def strategy_entry_signal(bar: Dict, ind: Dict, state: Dict, params: Dict) -> Optional[Dict]:
    """
    OLD FORMAT from smart-trade repo
    
    Returns:
        {
            "side": "LONG" | "SHORT",
            "reason": "Entry reason description",
            "regime_hint": "trend" | "range" | "breakout",
            "meta": {
                "sl_tp_style": "atr_fixed" | "chandelier" | "breakeven_then_trail",
                "sl_atr_mult": float,
                "tp_rr_multiple": float,
                "trail_atr_mult": float | None,
                "breakeven_at_R": float | None
            }
        }
    """
```

### Conversão para Novo Formato

```python
class StrategyName(BaseStrategy):
    """NEW FORMAT for Smart-Trade-MCP"""
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals = []
        position = None
        
        for i in range(1, len(df)):
            row = df.iloc[i]
            prev_row = df.iloc[i - 1]
            
            # Extract indicators
            close = row["close"]
            # ... other OHLCV and indicators
            
            # ENTRY LOGIC (from old format)
            if position is None:
                # LONG conditions
                if <conditions>:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    signals.append(Signal(
                        type=SignalType.LONG,
                        timestamp=row["timestamp"],
                        price=close,
                        confidence=<calculated>,
                        stop_loss=sl,
                        take_profit=tp,
                        metadata={"reason": "..."},
                    ))
                    position = "LONG"
                
                # SHORT conditions
                elif <conditions>:
                    # Similar for SHORT
                    pass
            
            # EXIT LOGIC
            elif position == "LONG":
                if <exit_conditions>:
                    signals.append(Signal(
                        type=SignalType.CLOSE_LONG,
                        timestamp=row["timestamp"],
                        price=close,
                        metadata={"reason": "exit"},
                    ))
                    position = None
        
        return signals
```

---

## ?? TOP 10 ESTRATÉGIAS (Priority 1)

Implementar estas primeiro por ordem de win rate:

| # | Nome | Win Rate | Categoria | Priority |
|---|------|----------|-----------|----------|
| 1 | `bollinger_mean_reversion` | 60-70% | Mean Reversion | ?? HIGH |
| 2 | `rsi_band_reversion` | 58-68% | Mean Reversion | ?? HIGH |
| 3 | `vwap_institutional_trend` | 58-68% | Hybrid | ?? HIGH |
| 4 | `ema200_tap_reversion` | 56-64% | Mean Reversion | HIGH |
| 5 | `ema_cloud_trend` | 50-60% | Trend Following | HIGH |
| 6 | `keltner_pullback_continuation` | 50-60% | Hybrid | HIGH |
| 7 | `donchian_continuation` | 40-50% | Trend Following | MEDIUM |
| 8 | `bollinger_squeeze_breakout` | 45-52% | Breakout | MEDIUM |
| 9 | `macd_zero_trend` | 45-52% | Trend Following | MEDIUM |
| 10 | `triple_momentum_confluence` | 48-56% | Momentum | MEDIUM |

---

## ?? IMPLEMENTAÇÃO DETALHADA

### Exemplo 1: Bollinger Mean Reversion (60-70% win rate!)

**Lógica do repo antigo:**
```python
def bollinger_mean_reversion_entry_signal(bar, ind, state, params):
    close = bar['close']
    bb_lower = ind.get('bb_lower', 0)
    bb_middle = ind.get('bb_middle', 0)
    bb_upper = ind.get('bb_upper', float('inf'))
    rsi14 = ind.get('rsi14', 50)
    
    # LONG: Price touches BB lower + RSI oversold
    if close <= bb_lower * 1.01 and rsi14 < 30 and close > ind.get('prev_low', 0):
        return {
            "side": "LONG",
            "reason": "BB lower + RSI oversold mean reversion",
            "meta": {"sl_atr_mult": 1.5, "tp_rr_multiple": 2.0}
        }
    
    # SHORT: Price touches BB upper + RSI overbought
    if close >= bb_upper * 0.99 and rsi14 > 70 and close < ind.get('prev_high', float('inf')):
        return {
            "side": "SHORT",
            "reason": "BB upper + RSI overbought mean reversion",
            "meta": {"sl_atr_mult": 1.5, "tp_rr_multiple": 2.0}
        }
```

**Converter para:**
```python
# src/strategies/generated/bollinger_mean_reversion.py

class BollingerMeanReversion(BaseStrategy):
    def get_required_indicators(self) -> List[str]:
        return ["bollinger", "rsi", "atr"]
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        signals = []
        position = None
        
        for i in range(1, len(df)):
            row = df.iloc[i]
            prev_row = df.iloc[i - 1]
            
            close = row["close"]
            bb_lower = row.get("bb_lower", 0)
            bb_upper = row.get("bb_upper", float('inf'))
            bb_middle = row.get("bb_middle", close)
            rsi = row.get("rsi", 50)
            atr = row.get("atr", close * 0.02)
            
            prev_low = prev_row["low"]
            prev_high = prev_row["high"]
            
            timestamp = row["timestamp"]
            
            # LONG entry
            if position is None:
                if close <= bb_lower * 1.01 and rsi < 30 and close > prev_low:
                    sl, tp = self.calculate_exit_levels(SignalType.LONG, close, atr)
                    
                    signals.append(Signal(
                        type=SignalType.LONG,
                        timestamp=timestamp,
                        price=close,
                        confidence=1.0 - (rsi / 100),  # Lower RSI = higher confidence
                        stop_loss=sl,
                        take_profit=tp,
                        metadata={
                            "rsi": rsi,
                            "bb_distance": ((bb_middle - close) / bb_middle) * 100,
                            "reason": "BB lower touch + RSI oversold",
                        },
                    ))
                    position = "LONG"
                
                # SHORT entry
                elif close >= bb_upper * 0.99 and rsi > 70 and close < prev_high:
                    sl, tp = self.calculate_exit_levels(SignalType.SHORT, close, atr)
                    
                    signals.append(Signal(
                        type=SignalType.SHORT,
                        timestamp=timestamp,
                        price=close,
                        confidence=(rsi - 50) / 50,
                        stop_loss=sl,
                        take_profit=tp,
                        metadata={
                            "rsi": rsi,
                            "bb_distance": ((close - bb_middle) / bb_middle) * 100,
                            "reason": "BB upper touch + RSI overbought",
                        },
                    ))
                    position = "SHORT"
            
            # Exit logic: Price returns to middle BB
            elif position == "LONG":
                if close >= bb_middle:
                    signals.append(Signal(
                        type=SignalType.CLOSE_LONG,
                        timestamp=timestamp,
                        price=close,
                        metadata={"reason": "BB mean reversion complete"},
                    ))
                    position = None
            
            elif position == "SHORT":
                if close <= bb_middle:
                    signals.append(Signal(
                        type=SignalType.CLOSE_SHORT,
                        timestamp=timestamp,
                        price=close,
                        metadata={"reason": "BB mean reversion complete"},
                    ))
                    position = None
        
        return signals
```

---

## ?? PRÓXIMOS PASSOS

### Fase 1: Implementar TOP 10 (Prioridade Máxima)
1. ? `bollinger_mean_reversion`
2. ? `rsi_band_reversion`
3. ? `vwap_institutional_trend`
4. ? `ema200_tap_reversion`
5. ? `ema_cloud_trend`
6. ? `keltner_pullback_continuation`
7. ? `donchian_continuation`
8. ? `bollinger_squeeze_breakout`
9. ? `macd_zero_trend`
10. ? `triple_momentum_confluence`

### Fase 2: Implementar Restantes 25
- Mean Reversion: 2 restantes
- Breakout: 7 restantes
- Momentum: 7 restantes
- Hybrid: 5 restantes
- Advanced: 6 restantes

### Fase 3: Testes & Validação
- Unit tests para cada estratégia
- Integration tests
- Backtest validation

### Fase 4: Otimização
- Parameter optimization
- Performance tuning

---

## ?? REFERÊNCIAS

### Ficheiros do Repo Antigo
- `C:\Users\shuta\desktop\smart-trade\strategies\mean_reversion.py`
- `C:\Users\shuta\desktop\smart-trade\strategies\trend_following.py`
- `C:\Users\shuta\desktop\smart-trade\strategies\breakout.py`
- `C:\Users\shuta\desktop\smart-trade\strategies\momentum.py`
- `C:\Users\shuta\desktop\smart-trade\strategies\hybrid.py`
- `C:\Users\shuta\desktop\smart-trade\strategies\advanced.py`

### Metadata
- `C:\Users\shuta\desktop\smart-trade\strategies\strategy_metadata.py`

---

## ? QUICK COMMANDS

```bash
# Generate all strategy files (already done)
poetry run python scripts/generate_all_strategies.py

# Test new indicators
poetry run pytest tests/unit/test_new_indicators.py -v

# Test all
poetry run pytest -v

# Run backtest with implemented strategy
poetry run python examples/simple_backtest.py
```

---

**Status:** ?? Em Progresso (14 indicadores ?, 3/38 estratégias)  
**Next:** Implementar TOP 10 estratégias com melhor win rate
