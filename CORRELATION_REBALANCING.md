# ?? CORRELATION-AWARE PORTFOLIO + AUTO-REBALANCING

**Version:** 4.1.0  
**Date:** 2025-11-22  
**Status:** ? Implemented

---

## ?? **O QUE FOI IMPLEMENTADO**

### **1. Correlation Analysis (4 Tools)**

```python
# Tool 1: Detect Symbol Correlations
correlations = await detect_symbol_correlations(
    symbols=["BTC/USDT", "ETH/USDT", "SOL/USDT", "MATIC/USDT"],
    timeframe="1h",
    lookback_days=30
)

# Response:
{
    "correlation_matrix": {
        "BTC/USDT": {"BTC/USDT": 1.0, "ETH/USDT": 0.87, ...},
        ...
    },
    "high_correlations": [
        {"pair1": "BTC/USDT", "pair2": "ETH/USDT", "correlation": 0.87}
    ],
    "diversification_score": 0.65,
    "recommendations": {
        "avoid_duplicate_strategies": ["BTC/USDT + ETH/USDT"],
        "good_diversification": ["BTC/USDT + MATIC/USDT"]
    }
}

# Tool 2: Get Diversification Recommendations
recommendations = await get_diversification_recommendations(
    active_agents=[...],
    candidate_symbols=["SOL/USDT", "MATIC/USDT", "DOT/USDT"]
)

# Response: Ranked candidates by diversification benefit
{
    "ranked_candidates": [
        {
            "symbol": "MATIC/USDT",
            "avg_correlation": 0.35,
            "diversification_benefit": "high"
        }
    ]
}
```

### **2. Auto-Rebalancing (2 Tools)**

```python
# Tool 3: Rebalance Portfolio
result = await rebalance_agent_portfolio(
    target_sharpe=1.5,
    min_agents=5,
    max_agents=12,
    min_win_rate=0.55,
    correlation_threshold=0.8
)

# Response:
{
    "actions_taken": {
        "stopped": [
            {"agent_id": "...", "reason": "Sharpe below target", ...}
        ],
        "kept": [...],
        "warnings": [
            "BTC and ETH both using same strategy (correlation 0.87)"
        ]
    },
    "portfolio_before": {"avg_sharpe": 1.2, ...},
    "portfolio_after": {"avg_sharpe": 1.8, "improvement": "+0.6"},
    "recommendations": [...]
}

# Tool 4: Suggest New Agents
suggestions = await suggest_new_agents(
    target_agent_count=10
)

# Response: Smart suggestions based on diversification
{
    "suggestions": [
        {
            "symbol": "MATIC/USDT",
            "recommended_strategy": "cci_extreme_snapback",
            "regime": "RANGING",
            "diversification_benefit": "high",
            "confidence": "high"
        }
    ]
}
```

---

## ?? **COMO CLAUDE USA**

### **Scenario 1: Lançar Novos Agentes com Diversificação**

```
CLAUDE:
"Vou analisar correlações antes de lançar os bots..."

# 1. Verificar correlações
correlations = await detect_symbol_correlations([
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "MATIC/USDT"
])

# Claude vê:
# - BTC e ETH: correlação 0.87 (muito alta!)
# - BTC e MATIC: correlação 0.35 (baixa - boa diversificação!)

# 2. Claude decide:
# ? Lançar ema_cloud_trend em BTC
# ? NÃO lançar ema_cloud_trend em ETH (mesma estratégia, alta correlação)
# ? Lançar bollinger_mean_rev em ETH (estratégia diferente)
# ? Lançar cci_snapback em MATIC (baixa correlação)

CLAUDE diz ao user:
"Lancei 3 bots com excelente diversificação:
- BTC/USDT: ema_cloud_trend
- ETH/USDT: bollinger_mean_rev (evitei duplicar estratégia com BTC)
- MATIC/USDT: cci_snapback (baixa correlação 0.35 com BTC/ETH)"
```

### **Scenario 2: Rebalancing Automático (Diário)**

```python
CLAUDE (a cada 24h):

# Executar rebalancing
result = await rebalance_agent_portfolio(
    target_sharpe=1.5,
    min_win_rate=0.55
)

# Claude analisa resultado:
{
    "stopped": [
        "agent_sol_atr_001" ? Sharpe 0.8 (abaixo de 1.5)
        "agent_avax_macd_002" ? Win rate 45% (abaixo de 55%)
    ],
    "warnings": [
        "BTC e ETH ambos usando ema_cloud (correlação 0.87)"
    ],
    "portfolio_improvement": "+0.6 Sharpe"
}

CLAUDE informa user:
"?? Rebalancing Diário Completo

Paragens (Performance Baixa):
- SOL/USDT (atr_breakout): Sharpe 0.8 ? PARADO
- AVAX/USDT (macd_zero): Win rate 45% ? PARADO

?? Aviso de Correlação:
- BTC e ETH ambos usando ema_cloud (correlação 0.87)
- Recomendação: Trocar estratégia em ETH

? Portfolio Melhorou:
- Sharpe médio: 1.2 ? 1.8 (+0.6)
- Total PnL: +$1,245 (após remover losers)
- Agentes ativos: 6 (todos com Sharpe > 1.5)"
```

### **Scenario 3: User Quer Adicionar Mais Bots**

```
USER:
"Claude, tenho 6 bots. Quero adicionar mais 4."

CLAUDE:
# Pedir sugestões inteligentes
suggestions = await suggest_new_agents(
    target_agent_count=10
)

# Recebe:
[
    {
        "symbol": "MATIC/USDT",
        "strategy": "bollinger_mean_rev",
        "diversification_benefit": "high",
        "correlation": 0.32  # Baixa!
    },
    {
        "symbol": "DOT/USDT",
        "strategy": "vwap_institutional",
        "diversification_benefit": "high",
        "correlation": 0.41
    },
    {
        "symbol": "LINK/USDT",
        "strategy": "cci_snapback",
        "diversification_benefit": "medium",
        "correlation": 0.58
    },
    {
        "symbol": "UNI/USDT",
        "strategy": "rsi_band_reversion",
        "diversification_benefit": "medium",
        "correlation": 0.62
    }
]

CLAUDE responde:
"Recomendo adicionar estes 4 bots para máxima diversificação:

1. MATIC/USDT - bollinger_mean_rev
   - Correlação 0.32 com portfolio atual (excelente!)
   - Regime: RANGING
   - Backtest: Sharpe 1.7

2. DOT/USDT - vwap_institutional
   - Correlação 0.41 (ótima diversificação)
   - Regime: TRENDING_UP
   - Backtest: Sharpe 2.1

3. LINK/USDT - cci_snapback
   - Correlação 0.58 (boa diversificação)
   - Regime: VOLATILE
   - Backtest: Sharpe 1.9

4. UNI/USDT - rsi_band_reversion
   - Correlação 0.62 (diversificação moderada)
   - Regime: RANGING
   - Backtest: Sharpe 1.6

Portfolio após adição:
- 10 bots (target alcançado)
- Diversificação score: 0.72 (excelente)
- Nenhuma correlação > 0.8
- Sharpe médio esperado: 1.85

Queres que lance estes 4 bots?"
```

---

## ?? **VANTAGENS**

### **1. Diversificação Real**
- ? Evita concentração em pares correlacionados
- ? Portfolio verdadeiramente diversificado
- ? Reduz risco sistémico

### **2. Performance Otimizada**
- ? Remove underperformers automaticamente
- ? Mantém apenas Sharpe > target
- ? Melhora Sharpe médio do portfolio

### **3. Conflict Detection**
- ? Detecta duplicate strategies em pares correlacionados
- ? Alerta Claude para ajustar
- ? Previne over-allocation

### **4. Automated Maintenance**
- ? Rebalancing periódico sem intervenção manual
- ? Claude mantém portfolio saudável 24/7
- ? User só é notificado de mudanças importantes

---

## ?? **EXEMPLO PRÁTICO COMPLETO**

### **Dia 1: User Inicia Sistema**

```
USER: "Claude, analisa 15 símbolos e lança bots"

CLAUDE:
1. Analisa correlações de 15 symbols
2. Agrupa por correlação:
   - Grupo A (correlação alta): BTC, ETH, BNB
   - Grupo B (correlação média): SOL, AVAX, DOT
   - Grupo C (correlação baixa): MATIC, LINK, UNI

3. Lança 1 bot por grupo com estratégias diferentes:
   - BTC: ema_cloud_trend
   - ETH: bollinger_mean_rev (diferente de BTC!)
   - BNB: vwap_institutional (diferente de BTC/ETH!)
   - SOL: cci_snapback
   - MATIC: rsi_band_reversion
   - LINK: atr_breakout

Result: 6 bots, diversificação score: 0.78 (excelente!)
```

### **Dia 7: Rebalancing Automático**

```
CLAUDE (automaticamente):

# Rebalancing
result = await rebalance_agent_portfolio()

Ações:
- PAROU: SOL (Sharpe 0.7), LINK (Win rate 42%)
- MANTEVE: BTC, ETH, BNB, MATIC (todos Sharpe > 1.5)
- AVISO: BTC e ETH correlação alta, mas estratégias diferentes ? OK

# Sugestões para substituir
suggestions = await suggest_new_agents(target_agent_count=6)

# Lança 2 novos em pares menos correlacionados:
- DOT/USDT: macd_zero_trend (correlação 0.43)
- ATOM/USDT: vwap_band_fade (correlação 0.38)

Portfolio após 7 dias:
- 6 bots ativos (BTC, ETH, BNB, MATIC, DOT, ATOM)
- Sharpe médio: 1.2 ? 1.9 (+0.7!)
- Diversificação: 0.78 ? 0.82
- Total PnL: +$2,345
```

---

## ? **STATUS**

```
? Correlation Analysis - COMPLETO
? Diversification Recommendations - COMPLETO
? Auto-Rebalancing - COMPLETO
? Agent Suggestions - COMPLETO

?? PRÓXIMO: Registrar tools no MCP server
```

---

**SISTEMA AGORA TEM INTELIGÊNCIA DE PORTFOLIO MANAGER PROFISSIONAL!** ???
