# ?? Claude Desktop - Quick Start Guide

## ? STATUS: MCP Server READY!

---

## ?? PASSOS PARA TESTAR:

### 1?? **Fechar Claude Desktop (se estiver aberto)**
   - Fechar completamente a aplicação
   - Verificar que não está a correr em background

### 2?? **Abrir Claude Desktop**
   - Abrir normalmente
   - Aguardar alguns segundos para carregar

### 3?? **Verificar se o MCP server está ligado**
   No Claude Desktop, verifica se aparece:
   - ?? **"smart-trade"** na lista de servers
   - ? Status: **Connected** (verde)

### 4?? **Testar Tools - Quick Test (2-3 min)**

Copia e cola isto no Claude Desktop:

```
Hey Claude! Quero testar o Smart Trade MCP server.

1. Por favor, lista todas as estratégias disponíveis (usa a tool list_strategies)

2. Depois, pega nos dados de mercado do BTC/USDT timeframe 1h, últimos 500 candles
   (usa get_market_data)

3. Se funcionou, diz-me quantas estratégias existem e mostra um resumo dos dados!
```

---

## ? EXPECTED RESULTS:

Se tudo funcionar, vais ver:
1. **Claude vai usar as tools automaticamente**
2. **Resultado das strategies** (41 estratégias)
3. **Dados de mercado** (500 candles de BTC/USDT)

---

## ?? TROUBLESHOOTING:

### ? Server não aparece:
- Restart Claude Desktop
- Verifica config em: `%APPDATA%\Claude\claude_desktop_config.json`
- Path deve ser: `C:\Users\shuta\source\repos\Smart-Trade-MCP`

### ? Connection failed:
- Corre: `python -m src.mcp_server.server` manualmente
- Verifica erros no terminal
- Confirma que todas as deps estão instaladas

### ? Tools não funcionam:
- Verifica logs do Claude Desktop (Settings ? Developer)
- Corre os testes unitários: `python test_complete_system.py`

---

## ?? NEXT STEPS (depois de funcionar):

1. ? Testar **Portfolio Optimization** tool
2. ? Testar **GA Optimization** tool  
3. ? Testar **N-Fold WFA** tool
4. ? Demo completo com workflow real

---

**?? Ready to test! Open Claude Desktop and start chatting!**
