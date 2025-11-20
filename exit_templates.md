# TEMPLATE DE EXIT LOGIC POR TIPO DE ESTRATEGIA

## BREAKOUT STRATEGIES:
```python
# Exit on opposite breakout (trend reversal)
elif pos == "LONG" and <opposite_breakout_condition>:
    signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close,
                        metadata={"reason": "Opposite breakout"}))
    pos = None

elif pos == "SHORT" and <opposite_breakout_condition>:
    signals.append(Signal(SignalType.CLOSE_SHORT, r["timestamp"], close,
                        metadata={"reason": "Opposite breakout"}))
    pos = None
```

## MOMENTUM STRATEGIES:
```python
# Exit when momentum reverses
elif pos == "LONG" and <bearish_momentum>:
    signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close,
                        metadata={"reason": "Momentum reversed"}))
    pos = None

elif pos == "SHORT" and <bullish_momentum>:
    signals.append(Signal(SignalType.CLOSE_SHORT, r["timestamp"], close,
                        metadata={"reason": "Momentum reversed"}))
    pos = None
```

## MEAN REVERSION STRATEGIES:
```python
# Exit when price returns to mean
elif pos == "LONG" and close >= <mean_level>:
    signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close,
                        metadata={"reason": "Returned to mean"}))
    pos = None

elif pos == "SHORT" and close <= <mean_level>:
    signals.append(Signal(SignalType.CLOSE_SHORT, r["timestamp"], close,
                        metadata={"reason": "Returned to mean"}))
    pos = None
```

## As 17 que precisam de correcao:

BREAKOUT (7):
- london_breakout_atr
- pure_price_action_donchian
- double_donchian_pullback
- complete_system_5x

MOMENTUM (6):
- mfi_impulse_momentum
- trend_volume_combo
- obv_trend_confirmation
- ema_stack_regime_flip
- rsi_supertrend_flip

VWAP/MEAN REVERSION (3):
- vwap_mean_reversion (parcial - falta SHORT exit)
- vwap_band_fade_pro (parcial - falta SHORT exit)
- order_flow_momentum_vwap

SPECIAL (4):
- keltner_pullback_continuation
- ema200_tap_reversion
- ny_session_fade
- obv_confirmation_breakout_plus
- regime_adaptive_core
