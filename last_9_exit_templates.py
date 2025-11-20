# ULTIMAS 9 ESTRATEGIAS - EXIT LOGIC A ADICIONAR

## 1. pure_price_action_donchian
elif pos == "LONG" and close < don_m:
    signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close, metadata={"reason": "Crossed Donchian middle"}))
    pos = None

## 2. vwap_institutional_trend (JA TEM EXIT - verificar)

## 3. order_flow_momentum_vwap
elif pos == "LONG" and (obv < obv_prev or close < vwap):
    signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close, metadata={"reason": "OBV reversed or VWAP cross"}))
    pos = None

## 4. keltner_pullback_continuation
elif pos == "LONG" and close < kc_l:
    signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close, metadata={"reason": "Exited Keltner channel"}))
    pos = None

## 5. ema200_tap_reversion
elif pos == "LONG" and abs(close - ema200) / ema200 > 0.02:
    signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close, metadata={"reason": "Moved away from EMA200"}))
    pos = None

## 6. double_donchian_pullback
elif pos == "LONG" and low < prev_don_l:
    signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close, metadata={"reason": "Opposite breakout"}))
    pos = None

## 7. obv_confirmation_breakout_plus
elif pos == "LONG" and obv < obv_prev:
    signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close, metadata={"reason": "OBV diverged"}))
    pos = None

## 8. ny_session_fade
elif pos == "LONG" and <opposite_extreme>:
    signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close, metadata={"reason": "Reached opposite extreme"}))
    pos = None

## 9. regime_adaptive_core
elif pos == "LONG" and <regime_change>:
    signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close, metadata={"reason": "Regime changed"}))
    pos = None

## 10. complete_system_5x
elif pos == "LONG" and <any_confirmation_fails>:
    signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close, metadata={"reason": "Confirmation failed"}))
    pos = None
"""

print("Templates prontos para aplicacao manual")
