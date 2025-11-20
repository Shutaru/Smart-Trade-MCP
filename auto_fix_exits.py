# -*- coding: utf-8 -*-
"""
Adicionar exit logic automaticamente nas estrategias restantes
"""

FIXES_TO_APPLY = {
    "channel_squeeze_plus": {
        "exit_condition": "close crosses BB middle (mean reversion complete)",
        "code": """
            # FIX: ADD EXIT LOGIC - exit when price returns to BB middle
            elif pos == "LONG" and close <= bb_m:
                signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close,
                                    metadata={"reason": "Returned to BB middle"}))
                pos = None
            
            elif pos == "SHORT" and close >= bb_m:
                signals.append(Signal(SignalType.CLOSE_SHORT, r["timestamp"], close,
                                    metadata={"reason": "Returned to BB middle"}))
                pos = None"""
    },
    
    "volatility_weighted_breakout": {
        "exit_condition": "opposite BB breakout or ADX drops",
        "code": """
            # FIX: ADD EXIT LOGIC - exit on opposite BB breakout
            elif pos == "LONG" and low < bb_l:
                signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close,
                                    metadata={"reason": "Opposite breakout"}))
                pos = None
            
            elif pos == "SHORT" and high > bb_u:
                signals.append(Signal(SignalType.CLOSE_SHORT, r["timestamp"], close,
                                    metadata={"reason": "Opposite breakout"}))
                pos = None"""
    },
    
    "london_breakout_atr": {
        "exit_condition": "opposite breakout",
        "code": """
            # FIX: ADD EXIT LOGIC - exit on opposite breakout
            elif pos == "LONG" and low < prev_low:
                signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close,
                                    metadata={"reason": "Opposite breakout"}))
                pos = None
            
            elif pos == "SHORT" and high > prev_high:
                signals.append(Signal(SignalType.CLOSE_SHORT, r["timestamp"], close,
                                    metadata={"reason": "Opposite breakout"}))
                pos = None"""
    },
    
    "pure_price_action_donchian": {
        "exit_condition": "price crosses Donchian middle",
        "code": """
            # FIX: ADD EXIT LOGIC
            don_m = r.get("donchian_middle", close)
            
            elif pos == "LONG" and close < don_m:
                signals.append(Signal(SignalType.CLOSE_LONG, r["timestamp"], close,
                                    metadata={"reason": "Crossed Donchian middle"}))
                pos = None"""
    }
}

for strategy, fix in FIXES_TO_APPLY.items():
    print(f"{strategy}:")
    print(f"  Exit: {fix['exit_condition']}")
    print()
