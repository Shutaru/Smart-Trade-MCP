#!/usr/bin/env python3
"""Quick fix for remaining strategies - replace hardcoded values"""

from pathlib import Path

fixes = {
    'stoch_signal_reversal.py': [
        ('stoch_k < 20', 'stoch_k < self.stoch_oversold'),
        ('stoch_k > 80', 'stoch_k > self.stoch_overbought'),
        ('stoch_d < 20', 'stoch_d < self.stoch_oversold'),
        ('stoch_d > 80', 'stoch_d > self.stoch_overbought'),
    ],
    'london_breakout_atr.py': [
        ('hour == 8', 'hour == self.london_start_hour'),
        ('hour >= 8 and hour < 12', 'hour >= self.london_start_hour and hour < self.london_end_hour'),
    ],
    'ny_session_fade.py': [
        ('hour >= 14', 'hour >= self.ny_start_hour'),
        ('hour < 20', 'hour < self.ny_end_hour'),
    ],
    'vwap_band_fade_pro.py': [
        ('rsi < 35', 'rsi < self.rsi_oversold'),
        ('rsi > 65', 'rsi > self.rsi_overbought'),
    ],
    'pure_price_action_donchian.py': [
        # This one uses donchian_period parameter
    ],
    'complete_system_5x.py': [
        # This one combines multiple indicators
    ],
}

strategies_dir = Path('src/strategies/generated')

for filename, replacements in fixes.items():
    filepath = strategies_dir / filename
    if not filepath.exists():
        print(f'? {filename} not found')
        continue
    
    content = filepath.read_text(encoding='utf-8')
    original = content
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    if content != original:
        filepath.write_text(content, encoding='utf-8')
        print(f'? Fixed {filename}')
    else:
        print(f'??  {filename} - no changes needed')

print('\n? Quick fixes completed!')
