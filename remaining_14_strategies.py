# -*- coding: utf-8 -*-
"""
LISTA DAS 14 ESTRATEGIAS RESTANTES SEM EXIT LOGIC

Para cada uma, preciso adicionar exit na invalidacao do sinal.
"""

STRATEGIES_NEED_FIX = {
    "pure_price_action_donchian": {
        "type": "breakout",
        "exit": "Exit quando price cruza Donchian middle"
    },
    "mfi_impulse_momentum": {
        "type": "momentum",
        "exit": "Exit quando MFI surge reverte"
    },
    "trend_volume_combo": {
        "type": "momentum",
        "exit": "Exit quando OBV reverte"
    },
    "obv_trend_confirmation": {
        "type": "momentum",
        "exit": "Exit quando OBV deixa de rising OU price cruza EMA200"
    },
    "ema_stack_regime_flip": {
        "type": "momentum",
        "exit": "Exit quando EMA stack desfaz"
    },
    "vwap_institutional_trend": {
        "type": "institutional",
        "exit": "Exit quando cruza VWAP oposto"
    },
    "order_flow_momentum_vwap": {
        "type": "momentum_vwap",
        "exit": "Exit quando OBV reverte OU VWAP cross oposto"
    },
    "keltner_pullback_continuation": {
        "type": "pullback",
        "exit": "Exit quando sai do Keltner channel"
    },
    "ema200_tap_reversion": {
        "type": "mean_reversion",
        "exit": "Exit quando afasta de EMA200"
    },
    "double_donchian_pullback": {
        "type": "pullback",
        "exit": "Exit em breakout oposto"
    },
    "obv_confirmation_breakout_plus": {
        "type": "breakout",
        "exit": "Exit quando OBV diverge"
    },
    "ny_session_fade": {
        "type": "fade",
        "exit": "Exit em extremo oposto"
    },
    "regime_adaptive_core": {
        "type": "adaptive",
        "exit": "Exit quando regime muda"
    },
    "complete_system_5x": {
        "type": "complex",
        "exit": "Exit quando qualquer confirmacao falha"
    },
    "rsi_supertrend_flip": {
        "type": "momentum",
        "exit": "Exit quando RSI/CCI/Stoch revertem"
    }
}

print(f"Total: {len(STRATEGIES_NEED_FIX)} estrategias")
print()
for name, info in STRATEGIES_NEED_FIX.items():
    print(f"{name}:")
    print(f"  Tipo: {info['type']}")
    print(f"  Exit: {info['exit']}")
    print()
