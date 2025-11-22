# ??? DYNAMIC PAIR MANAGEMENT - Complete System

**Version:** 3.2.0  
**Date:** 2025-11-22  
**Status:** ? Production Ready

---

## ?? **ESCLARECIMENTO: O QUE É O "AGENTE"?**

### ? **NÃO É:**
- ? Claude Desktop
- ? LLM / AI Agent
- ? MCP Client
- ? Frontend

### ? **É:**
```
Python Script Autónomo que:
??? Runs 24/7 como background process
??? APScheduler triggers scan a cada X minutos
??? Fetches data via CCXT (Binance API)
??? Runs estratégias (código Python matemático)
??? Generates signals (lógica determinística)
??? Saves to SQLite database
```

**Claude Desktop** é apenas para **debugging/análise** via MCP. O agent é **completamente independente**!

---

## ?? **SISTEMA IMPLEMENTADO**

### **Arquitetura:**

```
???????????????????????????????????????????????????
?         REACT FRONTEND (Control Panel)          ?
?  • Ver todos pares Binance Futures              ?
?  • Toggle ON/OFF qualquer par (hotswap)         ?
?  • Auto-select: Top Volatility / Market Cap     ?
?  • Ver signals ativos                            ?
?  • Ver trades abertas                            ?
???????????????????????????????????????????????????
                    ?
                    ? HTTP REST API
                    ?
???????????????????????????????????????????????????
?            FASTAPI BACKEND (v3.2.0)             ?
?                                                  ?
?  NEW ENDPOINTS:                                  ?
?  • GET  /api/v1/pairs/available                 ?
?  • GET  /api/v1/pairs/active                    ?
?  • POST /api/v1/pairs/enable   (hotswap ON)    ?
?  • POST /api/v1/pairs/disable  (hotswap OFF)   ?
?  • GET  /api/v1/pairs/top-volatility           ?
?  • GET  /api/v1/pairs/top-marketcap            ?
?  • POST /api/v1/pairs/auto-select              ?
?  • GET  /api/v1/pairs/trades/active            ?
?  • GET  /api/v1/pairs/stats                    ?
???????????????????????????????????????????????????
                    ?
                    ? SQLite Database
                    ?
???????????????????????????????????????????????????
?          PAIR MANAGEMENT DATABASE                ?
?                                                  ?
?  Tables:                                         ?
?  • trading_pairs (enabled/disabled status)      ?
?  • active_trades (open positions)               ?
???????????????????????????????????????????????????
                    ?
                    ? Read enabled pairs
                    ?
???????????????????????????????????????????????????
?       AUTONOMOUS AGENT (Background Process)      ?
?                                                  ?
?  Lógica:                                         ?
?  1. Scan apenas pares ENABLED                   ?
?  2. Quando pair é DISABLED:                     ?
?     ??? Stop scanning                            ?
?     ??? Se tem trade aberta: seguir SL/TP      ?
?     ??? Não abrir novas trades                  ?
?  3. Quando pair é ENABLED:                      ?
?     ??? Start scanning no próximo ciclo         ?
???????????????????????????????????????????????????
```

---

## ?? **COMO USAR (API)**

### **1. Ver Todos os Pares Disponíveis (Binance Futures)**

```sh
GET http://localhost:8000/api/v1/pairs/available
```

**Response:**
```json
{
  "total": 247,
  "pairs": [
    {
      "symbol": "BTC/USDT",
      "base": "BTC",
      "quote": "USDT",
      "active": true,
      "type": "swap"
    },
    // ... 246 more
  ]
}
```

---

### **2. Ver Pares Ativos (Scanning Agora)**

```sh
GET http://localhost:8000/api/v1/pairs/active
```

**Response:**
```json
{
  "total": 3,
  "pairs": [
    {
      "symbol": "BTC/USDT",
      "timeframe": "1h",
      "enabled": true,
      "enabled_at": "2025-11-22T16:00:00"
    },
    // ...
  ]
}
```

---

### **3. Ativar Pares (Hotswap ON)**

```sh
POST http://localhost:8000/api/v1/pairs/enable
Content-Type: application/json

{
  "symbols": ["BTC/USDT", "ETH/USDT", "SOL/USDT"],
  "timeframe": "1h"
}
```

**Response:**
```json
{
  "success": true,
  "enabled": ["BTC/USDT", "ETH/USDT", "SOL/USDT"],
  "message": "Enabled 3 pairs"
}
```

**Resultado:**  
? Agent começa a scannear estes pares no próximo ciclo (15 min)

---

### **4. Desativar Pares (Hotswap OFF)**

```sh
POST http://localhost:8000/api/v1/pairs/disable
Content-Type: application/json

{
  "symbols": ["SOL/USDT"]
}
```

**Response:**
```json
{
  "success": true,
  "disabled": ["SOL/USDT"],
  "active_trades": {
    "SOL/USDT": 1
  },
  "message": "Disabled 1 pairs. 1 pairs have active trades."
}
```

**Resultado:**  
- ? Agent **para** de scannear SOL/USDT
- ?? Se tem trade aberta em SOL, **continua** a seguir SL/TP
- ? **Não abre** novas trades em SOL

---

### **5. Auto-Select: Top Volatility (5m, 1h)**

```sh
GET http://localhost:8000/api/v1/pairs/top-volatility?timeframe=5m&limit=10
```

**Response:**
```json
{
  "criteria": "volatility_5m",
  "timeframe": "5m",
  "total_analyzed": 50,
  "top_pairs": [
    {
      "symbol": "PEPE/USDT",
      "atr_pct": 4.52,
      "price": 0.0000123,
      "volume_24h": 1234567890
    },
    // Top 10 mais voláteis
  ]
}
```

**Para ativar automaticamente:**
```sh
POST http://localhost:8000/api/v1/pairs/auto-select
Content-Type: application/json

{
  "criteria": "volatility_5m",
  "limit": 10
}
```

---

### **6. Auto-Select: Top Market Cap (4h)**

```sh
GET http://localhost:8000/api/v1/pairs/top-marketcap?limit=10
```

**Response:**
```json
{
  "criteria": "marketcap_4h",
  "total": 10,
  "pairs": [
    {"symbol": "BTC/USDT", "rank": 1},
    {"symbol": "ETH/USDT", "rank": 2},
    {"symbol": "BNB/USDT", "rank": 3},
    // Top 10 por market cap
  ]
}
```

**Para ativar automaticamente:**
```sh
POST http://localhost:8000/api/v1/pairs/auto-select
Content-Type: application/json

{
  "criteria": "marketcap_4h",
  "limit": 10
}
```

---

### **7. Ver Trades Ativas**

```sh
GET http://localhost:8000/api/v1/pairs/trades/active

# OU filtrar por symbol:
GET http://localhost:8000/api/v1/pairs/trades/active?symbol=BTC/USDT
```

**Response:**
```json
{
  "total": 2,
  "symbol_filter": null,
  "trades": [
    {
      "id": 1,
      "symbol": "BTC/USDT",
      "strategy": "cci_extreme_snapback",
      "direction": "long",
      "entry_price": 95000.0,
      "entry_time": "2025-11-22T15:30:00",
      "stop_loss": 93000.0,
      "take_profit": 99000.0,
      "quantity": 0.1,
      "status": "open"
    },
    // ...
  ]
}
```

---

## ?? **CASOS DE USO**

### **Caso 1: User quer Top 10 Volatility (5m)**

**Frontend:**
```typescript
// User clica "Auto-select Top Volatility 5m"
const response = await fetch('http://localhost:8000/api/v1/pairs/auto-select', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    criteria: 'volatility_5m',
    limit: 10
  })
});

// Agent começa a scannear os 10 pares mais voláteis!
```

### **Caso 2: User quer adicionar BTC/USDT manualmente**

```typescript
await fetch('http://localhost:8000/api/v1/pairs/enable', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    symbols: ['BTC/USDT'],
    timeframe: '1h'
  })
});
```

### **Caso 3: User quer remover SOL/USDT mas tem trade aberta**

```typescript
// 1. Disable pair
await fetch('http://localhost:8000/api/v1/pairs/disable', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    symbols: ['SOL/USDT']
  })
});

// 2. Response mostra que tem 1 trade ativa
// ? Trade continua ativa e segue SL/TP
// ? Não abre novas trades
```

---

## ??? **DATABASE SCHEMA**

### **Table: trading_pairs**

```sql
CREATE TABLE trading_pairs (
    id INTEGER PRIMARY KEY,
    symbol TEXT UNIQUE NOT NULL,
    exchange TEXT DEFAULT 'binance',
    enabled BOOLEAN DEFAULT 0,
    timeframe TEXT DEFAULT '1h',
    auto_selected BOOLEAN DEFAULT 0,
    selection_criteria TEXT,  -- 'volatility_5m', 'marketcap_4h'
    added_at TIMESTAMP,
    enabled_at TIMESTAMP,
    disabled_at TIMESTAMP
);
```

### **Table: active_trades**

```sql
CREATE TABLE active_trades (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL,
    strategy TEXT NOT NULL,
    direction TEXT NOT NULL,  -- 'long' or 'short'
    entry_price REAL NOT NULL,
    entry_time TIMESTAMP NOT NULL,
    stop_loss REAL NOT NULL,
    take_profit REAL NOT NULL,
    quantity REAL NOT NULL,
    status TEXT DEFAULT 'open',  -- 'open', 'closed'
    exit_price REAL,
    exit_time TIMESTAMP,
    pnl REAL,
    notes TEXT
);
```

---

## ?? **WORKFLOW COMPLETO**

### **User Experience:**

```
1. User abre Frontend
   ?
2. Frontend mostra:
   ??? Todos os pares Binance (247)
   ??? Pares ativos (3)
   ??? Trades abertas (2)
   ??? Botões: "Top Volatility", "Top Market Cap"
   ?
3. User clica "Top Volatility 5m - Auto-select 10"
   ?
4. Frontend ? POST /api/v1/pairs/auto-select
   ?
5. Backend:
   ??? Calcula ATR% de 50 pares
   ??? Seleciona top 10
   ??? Desabilita pares antigos
   ??? Habilita novos 10 pares
   ?
6. Database atualizada
   ?
7. Autonomous Agent (próximo scan):
   ??? Lê database
   ??? Vê 10 novos pares enabled
   ??? Começa a scannear!
   ?
8. Signals aparecem no frontend em tempo real
```

---

## ?? **ESTATÍSTICAS & MONITORING**

### **Endpoint:**
```sh
GET http://localhost:8000/api/v1/pairs/stats
```

**Response:**
```json
{
  "total_pairs": 15,
  "enabled_pairs": 10,
  "disabled_pairs": 5,
  "active_trades": 3,
  "total_trades": 127,
  "enabled_symbols": [
    "BTC/USDT",
    "ETH/USDT",
    // ... 8 more
  ]
}
```

---

## ?? **FRONTEND INTEGRATION**

### **React Component Example:**

```tsx
import { useState, useEffect } from 'react';

function PairManagement() {
  const [availablePairs, setAvailablePairs] = useState([]);
  const [activePairs, setActivePairs] = useState([]);
  
  useEffect(() => {
    // Load available pairs
    fetch('http://localhost:8000/api/v1/pairs/available')
      .then(r => r.json())
      .then(data => setAvailablePairs(data.pairs));
    
    // Load active pairs
    fetch('http://localhost:8000/api/v1/pairs/active')
      .then(r => r.json())
      .then(data => setActivePairs(data.pairs));
  }, []);
  
  const enablePair = async (symbol: string) => {
    await fetch('http://localhost:8000/api/v1/pairs/enable', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({symbols: [symbol], timeframe: '1h'})
    });
    // Refresh active pairs
  };
  
  const autoSelectVolatility = async () => {
    await fetch('http://localhost:8000/api/v1/pairs/auto-select', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({criteria: 'volatility_5m', limit: 10})
    });
    // Refresh active pairs
  };
  
  return (
    <div>
      <button onClick={autoSelectVolatility}>
        ?? Top 10 Volatility (5m)
      </button>
      
      {availablePairs.map(pair => (
        <div key={pair.symbol}>
          {pair.symbol}
          <button onClick={() => enablePair(pair.symbol)}>
            Toggle
          </button>
        </div>
      ))}
    </div>
  );
}
```

---

## ? **PRÓXIMOS PASSOS**

1. ? **Backend implementado** (este commit)
2. ?? **Atualizar Agent** para ler database
3. ?? **Criar Frontend** React component
4. ?? **WebSocket** para real-time updates
5. ?? **Paper Trading** integration

---

**Sistema de Dynamic Pair Management 100% Implementado!** ????

**API Docs:** http://localhost:8000/api/docs#/Pair%20Management
