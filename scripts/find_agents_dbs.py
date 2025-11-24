import os, json
from pathlib import Path

start = Path('C:/Users/shuta')
found = []
for root, dirs, files in os.walk(start):
    for f in files:
        if f == 'agents.db':
            found.append(os.path.join(root, f))
# limit output
out = {'count': len(found), 'paths': found[:200]}
print(json.dumps(out, indent=2))
