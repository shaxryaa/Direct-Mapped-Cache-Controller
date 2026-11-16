#!/usr/bin/env python3
"""Deterministic word-aligned traces; 0=read, 1=write; addresses are bytes."""
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]

def generate():
    rng = random.Random(2026)
    directed = [(0, a, 0) for a in (0, 4, 8, 12, 0, 1024, 0, 1008, 1020)]
    directed += [(1, 0, 0xDEADBEEF), (0, 0, 0), (1, 2048, 0x12345678),
                 (0, 2048, 0), (0, 2052, 0), (0, 0, 0),
                 (1, 65532, 0xCAFEBABE), (0, 65532, 0), (0, 65520, 0)]
    traces = {
        'directed': directed,
        'sequential': [(0, a, 0) for a in range(0, 4096, 4)],
        'repeated': [(0, a, 0) for _ in range(8) for a in range(0, 256, 4)],
        'conflict': [(0, a, 0) for _ in range(128) for a in (0, 1024)],
        'random': [(0, rng.randrange(16384)*4, 0) for _ in range(1024)],
        'mixed': [(int(rng.random() < .35), rng.randrange(2048)*4,
                   rng.getrandbits(32)) for _ in range(1024)],
        'write_stream': [(1, a, a ^ 0x76543210) for a in range(0, 1024, 4)]
                        + [(0, a, 0) for a in range(0, 1024, 4)],
        'all_offsets': [(0, base + offset, 0) for base in range(0, 1024, 16)
                        for offset in (12, 0, 8, 4)]
    }
    (ROOT / 'traces').mkdir(exist_ok=True)
    for name, rows in traces.items():
        (ROOT / 'traces' / (name+'.trace')).write_text(''.join(
            f'{op} {addr:08x} {data:08x}\n' for op, addr, data in rows))
    print(f'Generated {len(traces)} deterministic traces (seed 2026).')

if __name__ == '__main__':
    generate()
