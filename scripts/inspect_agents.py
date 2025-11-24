import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / 'data' / 'agents.db'
if not DB.exists():
    print('DB not found at', DB)
    raise SystemExit(1)

conn = sqlite3.connect(str(DB))
conn.row_factory = sqlite3.Row
cur = conn.cursor()
print('DB:', DB)
print('Agents:')
for r in cur.execute("SELECT agent_id, status, pid, started_at, stopped_at, stop_reason FROM agents ORDER BY created_at DESC"):
    row = dict(r)
    print(row)

print('\nActive agents from storage.get_active_agents()')
for r in cur.execute("SELECT agent_id, status, pid FROM agents WHERE status='active' ORDER BY created_at DESC"):
    print(dict(r))

print('\nStopped agents:')
for r in cur.execute("SELECT agent_id, status, pid FROM agents WHERE status='stopped' ORDER BY stopped_at DESC"):
    print(dict(r))

conn.close()
