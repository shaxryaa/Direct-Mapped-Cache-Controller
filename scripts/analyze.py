#!/usr/bin/env python3
"""Independently validate simulator CSVs and calculate reproducible metrics."""
import argparse
import csv
import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]

def analyze(name, cache_bytes=1024, block_bytes=16, suffix=''):
    trace = [tuple(int(v, 10 if i == 0 else 16) for i, v in enumerate(line.split()))
             for line in (ROOT/'traces'/f'{name}.trace').read_text().splitlines()]
    with (ROOT/'results'/f'{name}{suffix}.csv').open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len(trace) and rows, f'{name}: transaction count mismatch'
    tags, memory = {}, {}
    reads = writes = hits = read_misses = 0
    read_hit_latencies, read_miss_latencies = [], []
    for n, ((op, addr, data), row) in enumerate(zip(trace, rows)):
        block = addr // block_bytes
        index, tag = block % (cache_bytes // block_bytes), block // (cache_bytes // block_bytes)
        hit = tags.get(index) == tag
        expected = 0 if op else memory.get(addr, 0xA5A50000 ^ (addr//4))
        assert (int(row['request']), int(row['op']), int(row['address'],16),
                int(row['data'],16), int(row['hit'])) == (n,op,addr,expected,int(hit)), (name,n,row)
        if op:
            writes += 1
            memory[addr] = data
        else:
            reads += 1
            (read_hit_latencies if hit else read_miss_latencies).append(int(row['latency_cycles']))
            if not hit:
                read_misses += 1
                tags[index] = tag
        hits += hit
    # An explicit analytical model, distinct from simulated response latency:
    # 2-cycle read hit, 4 serial words * (request + 5 latency + consume),
    # 2 lookup cycles + 7 cycles for each write, no acceptance/CPU stalls.
    ideal_total = 2*reads + 7*(block_bytes//4)*read_misses + 9*writes
    return dict(workload=name, requests=len(rows), reads=reads, writes=writes, hits=hits,
                misses=len(rows)-hits, hit_rate=hits/len(rows), miss_rate=1-hits/len(rows),
                read_misses=read_misses, memory_read_words=read_misses*(block_bytes//4),
                memory_write_words=writes, ideal_amat_cycles=ideal_total/len(rows),
                measured_response_cycles=mean(int(r['latency_cycles']) for r in rows),
                measured_read_hit_cycles=mean(read_hit_latencies) if read_hit_latencies else None,
                measured_read_miss_cycles=mean(read_miss_latencies) if read_miss_latencies else None)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache-bytes',type=int,default=1024)
    parser.add_argument('--block-bytes',type=int,default=16)
    parser.add_argument('--suffix',default='')
    args=parser.parse_args()
    results=[analyze(p.stem,args.cache_bytes,args.block_bytes,args.suffix)
             for p in sorted((ROOT/'traces').glob('*.trace'))]
    dest=ROOT/'results'/f'summary{args.suffix}'
    dest.with_suffix('.json').write_text(json.dumps(results,indent=2)+'\n')
    with dest.with_suffix('.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(results[0]))
        writer.writeheader(); writer.writerows(results)
    lines=['# Verified performance results', '',
           f'Cache: {args.cache_bytes} bytes; block: {args.block_bytes} bytes. Rates include reads and writes.', '',
           '| Workload | Requests | Hits | Misses | Hit rate | Ideal AMAT (cycles) | Measured response (cycles) |',
           '|---|---:|---:|---:|---:|---:|---:|']
    for r in results:
        lines.append(f"| {r['workload']} | {r['requests']} | {r['hits']} | {r['misses']} | {r['hit_rate']:.2%} | {r['ideal_amat_cycles']:.3f} | {r['measured_response_cycles']:.3f} |")
    lines += ['', 'Ideal AMAT excludes memory acceptance stalls and CPU response backpressure. Measured response time includes both.',
              'See docs/REPORT.md for the timing derivation and workload interpretation.', '']
    dest.with_suffix('.md').write_text('\n'.join(lines))
    print('\n'.join(lines))

if __name__=='__main__':
    main()
