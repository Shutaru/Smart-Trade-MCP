# ?? GUIA DE TESTES RÁPIDOS - ASYNC JOBS

**Para:** Testes iniciais com Claude Desktop  
**Versão:** 3.0 - Com Async Optimization Jobs ?

---

## ? **SISTEMA DE JOBS ASSÍNCRONOS (ZERO TIMEOUT!)** ?

### **?? COMO FUNCIONA:**

```
1. START JOB (< 1s)
   ??> Devolve job_id, optimização corre em background

2. CHECK STATUS (< 1s, pode repetir)
   ??> Vê progresso: "Gen 8/20, Sharpe 1.8"

3. GET RESULTS (< 1s quando completo)
   ??> Resultados completos da optimização
```

### **? VANTAGENS:**

- **ZERO timeout** - Jobs correm em background
- **QUALIDADE MÁXIMA** - pop=50, gen=20 sem problemas  
- **MONITORIZÁVEL** - Claude vê progresso em tempo real
- **NÃO BLOQUEANTE** - Claude pode fazer outras coisas

---

## ?? **WORKFLOWS RECOMENDADOS**

### **Opção 1: Teste Simples (1 symbol) - ASYNC** ? **RECOMENDADO**

```
Claude, testa o sistema de trading AI-driven:

1. Analisa BTC/USDT no timeframe 1h
2. Detecta regime de mercado
3. Escolhe 3 melhores estratégias para o regime  
4. Compara estratégias (backtest)
5. INICIA JOB assíncrono de optimização da melhor:
   - População: 50
   - Gerações: 20
   - Usa: start_optimization_job()
   
6. Mostra-me o job_id

7. A cada 30 segundos, verifica progresso com get_optimization_job_status()

8. Quando status="COMPLETED", busca resultados com get_optimization_job_results()

9. Se Sharpe > 1.5, lança bot dedicado

IMPORTANTE: NÃO uses optimize_strategy_parameters() diretamente!
Usa o sistema de jobs assíncronos.
```

### **Opção 2: Teste Médio (3 symbols em paralelo)**

```
Claude, optimiza 3 estratégias EM PARALELO:

1. BTC/USDT ? Inicia job para cci_extreme_snapback
2. ETH/USDT ? Inicia job para bollinger_mean_reversion
3. MATIC/USDT ? Inicia job para ema_cloud_trend

Todos com pop=50, gen=20.

4. Mostra-me os 3 job_ids

5. Verifica progresso dos 3 jobs simultaneamente

6. À medida que completam, mostra resultados

7. Analisa correlações e lança bots nos promissores

QUALIDADE MÁXIMA, zero timeout, tudo em paralelo!
```

### **Opção 3: Teste Completo (5 symbols)**

```
Claude, sistema AI-driven completo:

Símbolos: BTC/USDT, ETH/USDT, SOL/USDT, MATIC/USDT, LINK/USDT

Workflow:
1. Análise de correlações entre todos
2. Detecta regime para cada um
3. Escolhe melhor estratégia por símbolo
4. INICIA 5 JOBS de optimização em paralelo
5. Monitoriza progresso de todos
6. Quando todos completarem:
   - Lança bots com Sharpe > 1.5
   - Evita duplicados (corr > 0.8)
   - Scan interval: 5 min

Resumo final:
- Bots lançados
- Diversificação score
- Sharpe médio
- Correlações
```

---

## ?? **FERRAMENTAS DISPONÍVEIS**

### **ASYNC OPTIMIZATION (SEM TIMEOUT!):**

| Tool | Descrição | Tempo |
|------|-----------|-------|
| `start_optimization_job()` | Inicia job em background | < 1s |
| `get_optimization_job_status()` | Verifica progresso | < 1s |
| `get_optimization_job_results()` | Busca resultados | < 1s |
| `list_optimization_jobs()` | Lista todos os jobs | < 1s |
| `cancel_optimization_job()` | Cancela job | < 1s |

### **OPTIMIZATION SINCR (PODE DAR TIMEOUT!):**

| Tool | Descrição | Tempo |
|------|-----------|-------|
| `optimize_strategy_parameters()` | Optimização bloqueante | 2-8 min ?? |

**?? RECOMENDAÇÃO:** Usa sempre os **ASYNC JOBS** para optimizações!

---

## ?? **EXEMPLOS PRÁTICOS**

### **Exemplo 1: Optimização Simples**

```python
# 1. START
job = start_optimization_job(
    strategy_name="cci_extreme_snapback",
    symbol="BTC/USDT",
    timeframe="1h",
    population_size=50,
    n_generations=20
)
# ? {"job_id": "opt_abc123", "estimated_time_minutes": 5}

# 2. CHECK (repetir até status="COMPLETED")
status = get_optimization_job_status("opt_abc123")
# ? {"status": "RUNNING", "progress_pct": 45, "best_sharpe": 1.8}

# 3. RESULTS
results = get_optimization_job_results("opt_abc123")
# ? Full optimization results
```

### **Exemplo 2: Múltiplos Jobs Paralelos**

```python
# Inicia 3 jobs
job1 = start_optimization_job("cci_extreme_snapback", "BTC/USDT")
job2 = start_optimization_job("bollinger_mean_reversion", "ETH/USDT")
job3 = start_optimization_job("ema_cloud_trend", "MATIC/USDT")

# Verifica todos
jobs = [job1["job_id"], job2["job_id"], job3["job_id"]]
for job_id in jobs:
    status = get_optimization_job_status(job_id)
    print(f"{job_id}: {status['progress_pct']}%")
```

---

## ?? **MONITORAMENTO**

### **Ver Jobs Ativos:**

```python
list_optimization_jobs(status="running")
```

### **Ver Jobs Completos:**

```python
list_optimization_jobs(status="completed", limit=10)
```

---

## ? **TESTE DE SUCESSO**

**Critérios:**

1. ? Jobs iniciam em < 1s
2. ? Status updates aparecem
3. ? Jobs completam com Sharpe > 0
4. ? Resultados são recuperáveis
5. ? Bots são lançados

---

## ?? **TROUBLESHOOTING**

### **Job não aparece nos logs:**
- **NORMAL!** Jobs correm em threads separadas
- Usa `get_optimization_job_status()` para monitorizar

### **Job demora muito:**
- Verifica `estimated_time_minutes` no start
- pop=50, gen=20 ? ~5-8 min esperado

### **Como cancelar job:**
```python
cancel_optimization_job("opt_abc123", "Too slow")
```

---

## ?? **MÉTRICAS DE PERFORMANCE**

| Operação | Tempo Esperado |
|----------|----------------|
| start_optimization_job | < 1s |
| get_job_status | < 1s |
| get_job_results | < 1s |
| Job completo (pop=50, gen=20) | 5-8 min |
| Job rápido (pop=20, gen=8) | 2-3 min |

---

**PRONTO PARA TESTES COM QUALIDADE MÁXIMA! ??**

Usa sempre **ASYNC JOBS** para optimizações pesadas!
