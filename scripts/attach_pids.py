#!/usr/bin/env python3
import sys
from pathlib import Path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from src.agent.agent_storage import AgentStorage
from datetime import datetime
import re
import requests

# Mapping - adjust if needed
mapping = {
    'agent_SOL_USDT_5m_multi_oscillator_confluence_03c7ba': 54464,
    'agent_SOL_USDT_5m_volume_shooter_a52613': 19480,
    'agent_SOL_USDT_5m_ema_stack_momentum_81a7db': 51432,
    'agent_SOL_USDT_5m_bollinger_squeeze_breakout_6a16b7': 17248,
}

storage = AgentStorage(Path(repo_root) / 'data' / 'agents.db')

attached = []
created = []
for aid, pid in mapping.items():
    existing = storage.get_agent(aid)
    if existing:
        try:
            storage.update_pid(aid, int(pid))
            storage.update_status(aid, 'active')
            attached.append((aid, pid, 'updated'))
        except Exception as e:
            attached.append((aid, pid, f'failed_update:{e}'))
    else:
        # Parse agent id for fields: agent_{SYMBOL}_{timeframe}_{strategy}_{suffix}
        m = re.match(r'^agent_(?P<symbol>[^_]+_[^_]+)_(?P<timeframe>[^_]+)_(?P<strategy>.+)_(?P<suffix>[a-f0-9]+)$', aid)
        if m:
            symbol = m.group('symbol').replace('_', '/')
            timeframe = m.group('timeframe')
            strategy = m.group('strategy')
        else:
            # fallback
            parts = aid.split('_')
            symbol = 'UNKNOWN'
            timeframe = 'UNKNOWN'
            strategy = 'UNKNOWN'
        cfg = {
            'agent_id': aid,
            'symbol': symbol,
            'timeframe': timeframe,
            'strategy': strategy,
            'params': {},
            'risk_per_trade': 0.02,
            'scan_interval_minutes': 5,
            'started_at': datetime.now()
        }
        try:
            storage.add_agent(cfg)
            storage.update_pid(aid, int(pid))
            attached.append((aid, pid, 'created'))
            created.append(aid)
        except Exception as e:
            attached.append((aid, pid, f'failed_create:{e}'))

print('Attach results:')
for r in attached:
    print(r)

# trigger restore endpoint
try:
    resp = requests.post('http://127.0.0.1:8000/api/v1/paper/bots/restore', timeout=5)
    print('Restore response:', resp.status_code, resp.text)
except Exception as e:
    print('Failed to call restore endpoint:', e)

print('Done')
