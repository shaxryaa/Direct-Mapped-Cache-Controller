#!/usr/bin/env python3
"""Check no-cache data/traffic against cache runs and compare measured latency."""
import csv
import json
from pathlib import Path
import re
from statistics import mean

R=Path(__file__).resolve().parents[1]
summary=[]
for path in sorted((R/'traces').glob('*.trace')):
    name=path.stem
    def load(suffix):
        with (R/'results'/f'{name}{suffix}.csv').open() as f:
            return list(csv.DictReader(f))
    cached, baseline=load(''),load('_baseline')
    assert len(cached)==len(baseline)>0
    for x,y in zip(cached,baseline):
        assert all(x[k]==y[k] for k in ('request','op','address','data'))
        assert y['hit']=='0'
    writes=sum(int(row['op']) for row in baseline)
    log=(R/'results'/f'{name}_baseline.log').read_text()
    count=re.search(r'memory_reads=(\d+) memory_writes=(\d+)',log)
    assert 'PASS requests=' in log
    assert count and tuple(map(int,count.groups()))==(len(baseline)-writes,writes)
    cache_time=mean(int(row['latency_cycles']) for row in cached)
    baseline_time=mean(int(row['latency_cycles']) for row in baseline)
    summary.append(dict(workload=name,requests=len(cached),cache_response_cycles=cache_time,
        baseline_response_cycles=baseline_time,response_speedup=baseline_time/cache_time))
(R/'results/baseline_comparison.json').write_text(json.dumps(summary,indent=2)+'\n')
lines=['# No-cache baseline comparison','',
       'Same traces, memory latency, memory ready schedule and CPU response-ready policy. Each run starts from reset.',
       'Speedup is baseline mean response latency divided by cache mean response latency; idle driver gaps are excluded.',
       'The no-cache controller retains the same request/lookup stages for a controlled comparison.','',
       '| Workload | Cache cycles | No-cache cycles | Response speedup |','|---|---:|---:|---:|']
for row in summary:
    lines.append(f"| {row['workload']} | {row['cache_response_cycles']:.3f} | {row['baseline_response_cycles']:.3f} | {row['response_speedup']:.3f}x |")
(R/'results/baseline_comparison.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
