import json
from pathlib import Path

def read_json(path):
    p = Path(path)
    if not p.exists():
        return []
    return json.loads(p.read_text())

def write_json(path, data):
    p = Path(path)
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(data, indent=2))
