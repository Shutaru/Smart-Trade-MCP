import sqlite3, json, sys
from pathlib import Path

db_path = Path(__file__).resolve().parents[1] / 'data' / 'agents.db'
if not db_path.exists():
    print(json.dumps({'error':'db not found', 'db_path': str(db_path)}))
    sys.exit(0)

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute('SELECT * FROM agents ORDER BY created_at DESC')
agents = [dict(r) for r in cur.fetchall()]
for a in agents:
    if a.get('params'):
        try:
            a['params'] = json.loads(a['params'])
        except Exception:
            pass

cur.execute('SELECT * FROM agent_trades ORDER BY entry_time DESC LIMIT 50')
trades = [dict(r) for r in cur.fetchall()]
cur.execute('SELECT * FROM agent_events ORDER BY created_at DESC LIMIT 200')
events = [dict(r) for r in cur.fetchall()]

print(json.dumps({'db_path': str(db_path), 'agents': agents, 'trades': trades, 'events': events}, default=str, indent=2))
conn.close()