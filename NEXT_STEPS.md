# ?? PRÓXIMOS PASSOS - Integração MCP Tools

**Status Atual:** ? Fase B (Correlation + Rebalancing) Completa

---

## ?? **FASE A: Registrar MCP Tools (PRÓXIMO)**

### **10 Novos Tools a Registrar em `server.py`:**

#### **Agent Management (6 tools):**
1. `launch_trading_agent` - Spawnar agente dedicado
2. `stop_trading_agent` - Parar agente
3. `list_active_agents` - Listar todos agentes
4. `get_agent_performance` - Métricas detalhadas
5. `update_agent_params` - Ajustar parâmetros
6. `get_agent_summary` - Portfolio summary

#### **Correlation & Rebalancing (4 tools):**
7. `detect_symbol_correlations` - Análise de correlações
8. `get_diversification_recommendations` - Sugestões diversificação
9. `rebalance_agent_portfolio` - Auto-rebalancing
10. `suggest_new_agents` - Sugestões inteligentes

---

## ? **IMPLEMENTADO (Commits já feitos):**

1. ? Agent Orchestrator
2. ? Trading Agent (dedicated)
3. ? Agent Storage (database)
4. ? Agent Management Tools (6)
5. ? Correlation Analysis Tools (2)
6. ? Auto-Rebalancing Tools (2)
7. ? Documentation completa

---

## ?? **PRÓXIMA TAREFA: Atualizar server.py**

### **Passo 1: Adicionar Tool Definitions**

Em `server.py`, linha ~51, mudar de 15 para 25 tools e adicionar definitions:

```python
logger.info("?? list_tools() called - returning 25 tools")

# ... (tools existentes)

# AGENT MANAGEMENT TOOLS (6)
Tool(
    name="launch_trading_agent",
    description="?? Launch dedicated autonomous trading agent for symbol/strategy",
    inputSchema={...}
),

Tool(name="stop_trading_agent", ...),
Tool(name="list_active_agents", ...),
Tool(name="get_agent_performance", ...),
Tool(name="update_agent_params", ...),
Tool(name="get_agent_summary", ...),

# CORRELATION & REBALANCING TOOLS (4)
Tool(name="detect_symbol_correlations", ...),
Tool(name="get_diversification_recommendations", ...),
Tool(name="rebalance_agent_portfolio", ...),
Tool(name="suggest_new_agents", ...),
```

### **Passo 2: Adicionar Imports**

```python
from .tools.agent_management import (
    launch_trading_agent,
    stop_trading_agent,
    list_active_agents,
    get_agent_performance,
    update_agent_params,
    get_agent_summary,
)

from .tools.correlation_analysis import (
    detect_symbol_correlations,
    get_diversification_recommendations,
)

from .tools.auto_rebalancing import (
    rebalance_agent_portfolio,
    suggest_new_agents,
)
```

### **Passo 3: Adicionar Handlers no `call_tool()`**

```python
# AGENT MANAGEMENT
elif name == "launch_trading_agent":
    result = await launch_trading_agent(**arguments)
elif name == "stop_trading_agent":
    result = await stop_trading_agent(**arguments)
elif name == "list_active_agents":
    result = await list_active_agents()
elif name == "get_agent_performance":
    result = await get_agent_performance(**arguments)
elif name == "update_agent_params":
    result = await update_agent_params(**arguments)
elif name == "get_agent_summary":
    result = await get_agent_summary()

# CORRELATION & REBALANCING
elif name == "detect_symbol_correlations":
    result = await detect_symbol_correlations(**arguments)
elif name == "get_diversification_recommendations":
    result = await get_diversification_recommendations(**arguments)
elif name == "rebalance_agent_portfolio":
    result = await rebalance_agent_portfolio(**arguments)
elif name == "suggest_new_agents":
    result = await suggest_new_agents(**arguments)
```

---

## ?? **NOTAS IMPORTANTES:**

1. **InputSchemas:** Criar schemas completos para cada tool (ver exemplos em `agent_management.py`)
2. **Testing:** Testar cada tool via Claude Desktop após registro
3. **Documentation:** Atualizar system instructions com novos workflows

---

## ?? **APÓS COMPLETAR FASE A:**

### **FASE C: Prompts Otimizados para Claude**

Criar guia de uso otimizado para Claude:

```markdown
### Workflow: Lançar Bots AI-Driven

USER: "Analisa 10 symbols e lança bots promissores"

CLAUDE:
1. Para cada symbol:
   - detect_market_regime()
   - compare_strategies(regime-appropriate)
   - optimize_strategy_parameters(best)
   
2. Antes de lançar:
   - detect_symbol_correlations(all_symbols)
   - Evitar duplicate strategies em pares correlacionados
   
3. Lançar agents:
   - launch_trading_agent() para cada
   
4. Monitor:
   - list_active_agents() (diário)
   - rebalance_agent_portfolio() (semanal)
```

---

## ? **QUANDO TUDO ESTIVER PRONTO:**

**Sistema Completo:**
- ? 25 MCP Tools
- ? AI-Driven Portfolio Management
- ? Correlation-Aware Diversification
- ? Auto-Rebalancing
- ? Multi-Agent Architecture
- ? Production-Ready

**Diferenciais:**
1. LLM como Portfolio Manager
2. Regime-Aware Strategy Selection
3. Correlation-Based Diversification
4. Automatic Performance Optimization
5. Fault-Tolerant Multi-Agent System

---

**PRÓXIMO PASSO:** Editar `server.py` para adicionar os 10 tools! ??
