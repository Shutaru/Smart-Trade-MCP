"""Fix variable scope bug in all strategies."""
import os
import re

STRATEGIES_DIR = r"C:\Users\shuta\Desktop\Smart-Trade-MCP-CLEAN\src\strategies\generated"

# Files with the bug
BUGGY_FILES = [
    "atr_expansion_breakout.py",
    "channel_squeeze_plus.py",
    "double_donchian_pullback.py",
    "ema200_tap_reversion.py",
    "ema_stack_regime_flip.py",
    "keltner_pullback_continuation.py",
    "london_breakout_atr.py",
    "obv_confirmation_breakout_plus.py",
    "order_flow_momentum_vwap.py",
    "pure_price_action_donchian.py",
    "regime_adaptive_core.py",
    "volatility_weighted_breakout.py",
    "vwap_band_fade_pro.py",
    "vwap_breakout.py",
    "vwap_institutional_trend.py",
    "vwap_mean_reversion.py",
]

def fix_file(filepath):
    """Fix variable scope bug in a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Pattern: close, ..., ... = r["close"], ..., r.get(..., close)
    # Fix: Extract close first, then use it
    
    # Find lines like: close, x, y = r["close"], r.get("x", close), ...
    # Replace with: close = r["close"]; x, y = r.get("x", close), ...
    
    # More robust: find the problematic pattern and split it
    pattern = r'(\s+)(close[^=]*)(=\s*)(r\["close"\])(.*r\.get\([^,]+,\s*close)'
    
    def replace_func(match):
        indent = match.group(1)
        vars_before = match.group(2).strip()
        equals = match.group(3)
        r_close = match.group(4)
        rest = match.group(5)
        
        # Split into two lines
        # Line 1: close = r["close"]
        # Line 2: other vars
        
        # Extract variable names before 'close'
        vars_list = [v.strip() for v in vars_before.split(',')]
        vars_list = [v for v in vars_list if v]  # Remove empty
        
        if 'close' in vars_list:
            vars_list.remove('close')
        
        # Extract rest of assignments
        rest_cleaned = rest.strip()
        if rest_cleaned.startswith(','):
            rest_cleaned = rest_cleaned[1:].strip()
        
        # Build fixed code
        line1 = f"{indent}close = r[\"close\"]\n"
        
        if vars_list and rest_cleaned:
            line2 = f"{indent}{', '.join(vars_list)} = {rest_cleaned}\n"
            return line1 + line2
        else:
            return line1
    
    # Try simpler approach: just extract close first
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Check if line has the pattern
        if 'close' in line and '= r["close"]' in line and 'r.get(' in line and ', close)' in line:
            # This line has the bug
            # Extract indent
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent
            
            # Simple fix: split into two lines
            # Line 1: close = r["close"]
            fixed_lines.append(f"{indent_str}close = r[\"close\"]")
            
            # Line 2: rest of variables (remove close from left side)
            # Find everything after first =
            parts = line.split('=', 1)
            if len(parts) == 2:
                left_side = parts[0].strip()
                right_side = parts[1].strip()
                
                # Remove 'close' from left side
                left_vars = [v.strip() for v in left_side.split(',')]
                left_vars = [v for v in left_vars if v and v != 'close']
                
                # Remove r["close"] from right side
                right_parts = right_side.split(',', 1)
                if len(right_parts) == 2:
                    new_right = right_parts[1].strip()
                    if left_vars and new_right:
                        fixed_lines.append(f"{indent_str}{', '.join(left_vars)} = {new_right}")
        else:
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Fix all files
fixed_count = 0
for filename in BUGGY_FILES:
    filepath = os.path.join(STRATEGIES_DIR, filename)
    if os.path.exists(filepath):
        if fix_file(filepath):
            print(f"? Fixed: {filename}")
            fixed_count += 1
        else:
            print(f"??  No changes: {filename}")
    else:
        print(f"? Not found: {filename}")

print(f"\n? Fixed {fixed_count}/{len(BUGGY_FILES)} files")
