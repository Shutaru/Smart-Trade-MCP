import sqlite3
from pathlib import Path
import json

repo_db = Path(__file__).resolve().parents[1] / 'data' / 'agents.db'
other_db = Path.home() / 'AppData' / 'Local' / 'AnthropicClaude' / 'app-1.0.734' / 'data' / 'agents.db'

if not repo_db.exists():
    print(f"Repo DB not found at {repo_db}")
    raise SystemExit(1)

if not other_db.exists():
    print(f"Other DB not found at {other_db}")
    raise SystemExit(1)

print(f"Merging agents from {other_db} into {repo_db}")

def to_dict(row):
    return {k: row[k] for k in row.keys()}

with sqlite3.connect(str(repo_db)) as rconn, sqlite3.connect(str(other_db)) as oconn:
    rconn.row_factory = sqlite3.Row
    oconn.row_factory = sqlite3.Row
    rc = rconn.cursor()
    oc = oconn.cursor()

    # For each agent in other_db, if not exists in repo_db, insert
    oc.execute('SELECT * FROM agents')
    others = oc.fetchall()
    inserted = 0
    for a in others:
        aid = a['agent_id']
        rc.execute('SELECT 1 FROM agents WHERE agent_id = ?', (aid,))
        if rc.fetchone():
            # exists -> skip
            continue
        params = a['params'] if 'params' in a.keys() else None
        rc.execute('''
            INSERT INTO agents (agent_id, symbol, timeframe, strategy, params, risk_per_trade, scan_interval_minutes, status, created_at, started_at, stopped_at, stop_reason, last_heartbeat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            a['agent_id'], a['symbol'], a['timeframe'], a['strategy'], params, a['risk_per_trade'], a['scan_interval_minutes'], a['status'], a['created_at'], a['started_at'], a['stopped_at'], a['stop_reason'], a['last_heartbeat']
        ))
        inserted += 1

    # copy trades if agent not present in repo trades
    oc.execute('SELECT * FROM agent_trades')
    trades = oc.fetchall()
    t_inserted = 0
    for t in trades:
        # check if trade id exists in repo
        rc.execute('SELECT 1 FROM agent_trades WHERE id = ? AND agent_id = ?', (t['id'], t['agent_id']))
        if rc.fetchone():
            continue
        rc.execute('''
            INSERT INTO agent_trades (id, agent_id, symbol, direction, entry_price, entry_time, stop_loss, take_profit, quantity, exit_price, exit_time, pnl, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            t['id'], t['agent_id'], t['symbol'], t['direction'], t['entry_price'], t['entry_time'], t['stop_loss'], t['take_profit'], t['quantity'], t['exit_price'], t['exit_time'], t['pnl'], t['status'], t['notes']
        ))
        t_inserted += 1

    # copy events similarly
    oc.execute('SELECT * FROM agent_events')
    events = oc.fetchall()
    e_inserted = 0
    for ev in events:
        rc.execute('SELECT 1 FROM agent_events WHERE id = ? AND agent_id = ?', (ev['id'], ev['agent_id']))
        if rc.fetchone():
            continue
        rc.execute('''
            INSERT INTO agent_events (id, agent_id, event_type, event_data, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (ev['id'], ev['agent_id'], ev['event_type'], ev['event_data'], ev['created_at']))
        e_inserted += 1

    rconn.commit()

print(f"Inserted agents: {inserted}, trades: {t_inserted}, events: {e_inserted}")
