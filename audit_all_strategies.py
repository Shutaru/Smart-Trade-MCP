# -*- coding: utf-8 -*-
"""
AUDITORIA COMPLETA - Verificar exit logic de TODAS as 38 estrategias

Verifica se cada estrategia tem:
1. Entry conditions claras
2. Exit na invalidacao do sinal OU sinal contrario
3. Nenhum overtrading
"""

import os
import re

STRATEGIES_DIR = "C:\\Users\\shuta\\Desktop\\Smart-Trade-MCP-CLEAN\\src\\strategies\\generated"

def audit_strategy_file(filepath):
    """Audita um arquivo de estrategia para verificar exit logic."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    strategy_name = os.path.basename(filepath).replace('.py', '')
    
    # Check for position tracking
    has_pos_variable = 'pos = []' in content or 'position = None' in content or 'pos = None' in content
    
    # Check for entry signals
    has_long_entry = 'SignalType.LONG' in content and 'pos = "LONG"' in content
    has_short_entry = 'SignalType.SHORT' in content and 'pos = "SHORT"' in content
    
    # Check for exit signals
    has_long_exit = 'SignalType.CLOSE_LONG' in content or ('pos == "LONG"' in content and 'pos = None' in content)
    has_short_exit = 'SignalType.CLOSE_SHORT' in content or ('pos == "SHORT"' in content and 'pos = None' in content)
    
    # Count elif statements for exit logic
    exit_elif_count = len(re.findall(r'elif\s+pos\s*==\s*"(LONG|SHORT)"', content))
    
    # Check if exits reset position
    has_pos_reset = 'pos = None' in content
    
    # Determine status
    if has_long_entry and has_short_entry:
        if has_long_exit and has_short_exit and has_pos_reset:
            status = "? COMPLETO"
        elif has_pos_reset:
            status = "??  EXIT PARCIAL"
        else:
            status = "? SEM EXIT"
    elif has_long_entry or has_short_entry:
        if has_pos_reset:
            status = "??  APENAS 1 DIRECAO"
        else:
            status = "? SEM EXIT"
    else:
        status = "? NAO USA POS"
    
    return {
        'name': strategy_name,
        'status': status,
        'has_long_entry': has_long_entry,
        'has_short_entry': has_short_entry,
        'has_long_exit': has_long_exit,
        'has_short_exit': has_short_exit,
        'exit_elif_count': exit_elif_count,
        'has_pos_reset': has_pos_reset
    }

def main():
    print("=" * 100)
    print("AUDITORIA COMPLETA - EXIT LOGIC DAS 38 ESTRATEGIAS")
    print("=" * 100)
    print()
    
    # Get all strategy files
    strategy_files = [f for f in os.listdir(STRATEGIES_DIR) if f.endswith('.py') and f != '__init__.py']
    strategy_files.sort()
    
    results = []
    
    print(f"{'#':<4} {'Estrategia':<45} {'Status':<20} {'Exit Elif':<10}")
    print("-" * 100)
    
    for i, filename in enumerate(strategy_files, 1):
        filepath = os.path.join(STRATEGIES_DIR, filename)
        result = audit_strategy_file(filepath)
        results.append(result)
        
        print(f"{i:<4} {result['name']:<45} {result['status']:<20} {result['exit_elif_count']:<10}")
    
    print("-" * 100)
    print()
    
    # Summary
    complete = [r for r in results if r['status'] == "? COMPLETO"]
    partial = [r for r in results if r['status'].startswith("??")]
    missing = [r for r in results if r['status'].startswith("?")]
    other = [r for r in results if r['status'].startswith("?")]
    
    print("RESUMO:")
    print(f"  ? COMPLETO (com exit logic):     {len(complete)}/{len(results)}")
    print(f"  ??  PARCIAL (exit incompleto):     {len(partial)}/{len(results)}")
    print(f"  ? SEM EXIT (precisa correcao):   {len(missing)}/{len(results)}")
    print(f"  ? OUTRO (nao usa pos tracking):  {len(other)}/{len(results)}")
    print()
    
    if missing:
        print("ESTRATEGIAS SEM EXIT (PRECISAM CORRECAO):")
        for r in missing:
            print(f"  - {r['name']}")
        print()
    
    if partial:
        print("ESTRATEGIAS COM EXIT PARCIAL (VERIFICAR):")
        for r in partial:
            print(f"  - {r['name']}")
        print()
    
    return results

if __name__ == "__main__":
    main()
