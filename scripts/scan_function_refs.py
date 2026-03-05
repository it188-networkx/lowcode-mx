#!/usr/bin/env python3
"""扫描所有工作流 JSON，提取函数引用及参数。"""
import json, os, glob
from collections import defaultdict

wf_dir = os.path.join(os.path.dirname(__file__), '../../dev.dms/mx/workflow/')
files = sorted(glob.glob(os.path.join(wf_dir, '*.json')))

func_refs = defaultdict(list)

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    wfs = data.get('workflows', [])
    for wf in wfs:
        handle = wf.get('handle', '') or wf.get('meta', {}).get('name', os.path.basename(fpath))
        for step in wf.get('steps', []):
            if step.get('kind') == 'function' and step.get('ref'):
                ref = step['ref']
                args = step.get('arguments', [])
                results = step.get('results', [])
                func_refs[ref].append({
                    'handle': handle,
                    'file': os.path.basename(fpath),
                    'arguments': args,
                    'results': results,
                })

print(f'Total: {len(files)} workflow files')
print(f'Found: {len(func_refs)} distinct function refs\n')

for ref in sorted(func_refs.keys()):
    usages = func_refs[ref]
    arg_targets = defaultdict(set)
    res_targets = defaultdict(set)
    used_in = set()
    for u in usages:
        used_in.add(u['handle'])
        for a in u['arguments']:
            t = a.get('target', '')
            tp = a.get('type', '')
            val = a.get('value', a.get('expr', ''))
            if isinstance(val, str) and len(val) > 80:
                val = val[:80] + '...'
            arg_targets[t].add((tp, str(val)))
        for r in u['results']:
            t = r.get('target', '')
            tp = r.get('type', '')
            expr = r.get('expr', '')
            res_targets[t].add((tp, expr))

    print(f'=== {ref} === ({len(usages)} usages in {len(used_in)} workflows)')
    print(f'  Arguments:')
    for t in sorted(arg_targets.keys()):
        samples = arg_targets[t]
        types = sorted(set(s[0] for s in samples))
        vals = sorted(set(s[1] for s in samples))[:3]
        print(f'    target={t!r:30s}  types={types}  samples={vals}')
    print(f'  Results:')
    if res_targets:
        for t in sorted(res_targets.keys()):
            samples = res_targets[t]
            print(f'    target={t!r:30s}  {samples}')
    else:
        print(f'    (none)')
    print()
