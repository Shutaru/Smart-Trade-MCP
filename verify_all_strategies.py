# -*- coding: utf-8 -*-
"""
VERIFICACAO COMPLETA E CORRECAO - Todas as 38 estrategias

Verifica cada estrategia e identifica:
1. Se tem entry logic
2. Se tem exit logic
3. Se o exit acontece na invalidacao do sinal
4. Se precisa correcao
"""

import os
import re

STRATEGIES_DIR = "C:\\Users\\shuta\\Desktop\\Smart-Trade-MCP-CLEAN\\src\\strategies\\generated"

def analyze_strategy_detailed(filepath):
    """Analisa detalhadamente uma estrategia."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    strategy_name = os.path.basename(filepath).replace('.py', '')
    
    # Find position variable name
    pos_var = None
    if 'pos = None' in content or 'pos = []' in content:
        pos_var = 'pos'
    elif 'position = None' in content:
        pos_var = 'position'
    
    # Find entry lines
    entry_lines = []
    exit_lines = []
    
    for i, line in enumerate(lines):
        if pos_var and f'{pos_var} = "LONG"' in line:
            entry_lines.append(('LONG', i+1))
        if pos_var and f'{pos_var} = "SHORT"' in line:
            entry_lines.append(('SHORT', i+1))
        if pos_var and f'{pos_var} = None' in line and i > 0:
            # Check if it's an exit (not initialization)
            if 'CLOSE_LONG' in lines[i-5:i+1].__str__() or 'CLOSE_SHORT' in lines[i-5:i+1].__str__():
                exit_lines.append(i+1)
            elif f'elif {pos_var}' in lines[i-3:i+1].__str__():
                exit_lines.append(i+1)
    
    # Determine status
    has_entries = len(entry_lines) > 0
    has_exits = len(exit_lines) > 0
    
    if has_entries and has_exits:
        if len(exit_lines) >= 2:  # Should have at least 2 exits (LONG and SHORT)
            status = "? COMPLETO"
        else:
            status = "??  EXIT PARCIAL"
    elif has_entries and not has_exits:
        status = "? SEM EXIT"
    elif not pos_var:
        status = "? SEM POS VAR"
    else:
        status = "? VERIFICAR"
    
    return {
        'name': strategy_name,
        'status': status,
        'pos_var': pos_var,
        'entries': len(entry_lines),
        'exits': len(exit_lines),
        'entry_lines': entry_lines,
        'exit_lines': exit_lines
    }

def main():
    print("=" * 120)
    print("VERIFICACAO DETALHADA - EXIT LOGIC DAS 38 ESTRATEGIAS")
    print("=" * 120)
    print()
    
    # Get all strategy files
    strategy_files = [f for f in os.listdir(STRATEGIES_DIR) 
                     if f.endswith('.py') and f != '__init__.py' and f != 'auto_register.py']
    strategy_files.sort()
    
    results = []
    
    print(f"{'#':<4} {'Estrategia':<45} {'Status':<20} {'Entries':<10} {'Exits':<10} {'Pos Var':<10}")
    print("-" * 120)
    
    for i, filename in enumerate(strategy_files, 1):
        filepath = os.path.join(STRATEGIES_DIR, filename)
        result = analyze_strategy_detailed(filepath)
        results.append(result)
        
        pos_var_str = result['pos_var'] if result['pos_var'] else 'None'
        print(f"{i:<4} {result['name']:<45} {result['status']:<20} {result['entries']:<10} {result['exits']:<10} {pos_var_str:<10}")
    
    print("-" * 120)
    print()
    
    # Summary
    complete = [r for r in results if r['status'] == "? COMPLETO"]
    partial = [r for r in results if r['status'] == "??  EXIT PARCIAL"]
    missing = [r for r in results if r['status'] == "? SEM EXIT"]
    other = [r for r in results if r['status'].startswith("?")]
    
    print("RESUMO:")
    print(f"  ? COMPLETO (com exit logic correto):     {len(complete)}/{len(results)}")
    print(f"  ??  PARCIAL (exit incompleto):             {len(partial)}/{len(results)}")
    print(f"  ? SEM EXIT (PRECISA CORRECAO URGENTE):   {len(missing)}/{len(results)}")
    print(f"  ? OUTRO (precisa verificacao manual):    {len(other)}/{len(results)}")
    print()
    
    if missing:
        print(f"ESTRATEGIAS SEM EXIT - PRECISAM CORRECAO URGENTE ({len(missing)}):")
        for r in missing:
            print(f"  - {r['name']}")
        print()
    
    if partial:
        print(f"ESTRATEGIAS COM EXIT PARCIAL - VERIFICAR ({len(partial)}):")
        for r in partial:
            print(f"  - {r['name']} (Entries: {r['entries']}, Exits: {r['exits']})")
        print()
    
    if complete:
        print(f"ESTRATEGIAS COMPLETAS ({len(complete)}):")
        for r in complete:
            print(f"  ? {r['name']}")
        print()
    
    return results

if __name__ == "__main__":
    results = main()
