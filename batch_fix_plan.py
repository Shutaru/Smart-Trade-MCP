# -*- coding: utf-8 -*-
"""
BATCH FIX para estrategias com 1 trade
Aplica correcoes padrao para aumentar frequencia
"""

# Lista de correcoes a fazer:
FIXES_TO_APPLY = """
1. atr_expansion_breakout - Precisa ATR > avg*1.5, muito restritivo ? relaxar para 1.3
2. channel_squeeze_plus - Squeeze detection muito apertado ? relaxar bandwidth threshold
3. volatility_weighted_breakout - ADX >= 20 ? relaxar para >= 15
4. london_breakout_atr - Horario especifico Londres ? remover filtro horario (crypto 24/7)
5. triple_momentum_confluence - 3 indicadores simultaneos ? relaxar para 2 de 3
6. mfi_impulse_momentum - MFI extremos ? relaxar thresholds
7. trend_volume_combo - Volume 1.5x avg ? relaxar para 1.2x
8. obv_trend_confirmation - OBV rising + close > ema200 ? remover filtro EMA
9. ema_stack_regime_flip - Stack completo ? relaxar para partial stack
10. vwap_institutional_trend - VWAP cross + ema200 ? remover filtro EMA
11. order_flow_momentum_vwap - OBV + VWAP ? relaxar OBV threshold
12. keltner_pullback_continuation - Pullback exato ? relaxar zona de pullback
13. ema200_tap_reversion - Tap EMA200 exato ? relaxar para "near" EMA200
14. double_donchian_pullback - 2 timeframes ? simplificar para 1 timeframe
15. ny_session_fade - Horario NY ? remover filtro horario
16. regime_adaptive_core - Deteccao regime complexa ? simplificar
17. complete_system_5x - 5 confirmacoes ? reduzir para 3 confirmacoes

MANTEM COM 1 TRADE (estrategias conservadoras OK):
- rsi_supertrend_flip (100% WR, conservadora é bom)
- pure_price_action_donchian (ja corrigida antes)
- donchian_volatility_breakout (ja corrigida antes)
- obv_confirmation_breakout_plus (especifica para OBV divergence, OK ser rara)
"""

print(FIXES_TO_APPLY)
print()
print("Aplicando correcoes em batch...")
print()
