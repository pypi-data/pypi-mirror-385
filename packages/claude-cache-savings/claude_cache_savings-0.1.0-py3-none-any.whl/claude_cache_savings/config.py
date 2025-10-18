import json
import os
import sys
from pathlib import Path

FILE = Path(os.path.expanduser('.config/claude-cache-savings/config.json'))

def ensure_config_persisted(pricing:dict, models:dict):
    """ Only serialize the config initially, so as not to over-write any changes user might have made """
    if FILE.exists():
        return

    doc = dict(pricing=pricing, models=models)

    FILE.parent.mkdir(parents=True, exist_ok=True)
    with FILE.open('wt') as f:
        json.dump(doc, f, indent=2)

    print(f'[*] Model and pricing config file saved: {FILE}', file=sys.stderr)

def load_config():
    with FILE.open('rt') as f:
        doc = json.load(f)
    return doc['pricing'], doc['models']
