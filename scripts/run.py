#!/usr/bin/env python3
"""One-command simulation, independent result validation, and generic synthesis."""
import argparse
from pathlib import Path
import shutil
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def run(args, logfile=None):
    print('+', ' '.join(str(a) for a in args), flush=True)
    proc=subprocess.run([str(a) for a in args],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if logfile:
        (ROOT/logfile).write_text(proc.stdout)
    print(proc.stdout,end='')
    if proc.returncode:
        raise SystemExit(proc.returncode)
    return proc.stdout

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--skip-synthesis',action='store_true')
    args=parser.parse_args()
    needed=['iverilog','vvp']+([] if args.skip_synthesis else ['yosys'])
    for tool in needed:
        if not shutil.which(tool):
            raise SystemExit(f'Missing {tool}. See README.md for installation instructions.')
    for folder in ('build','results','traces'):
        (ROOT/folder).mkdir(exist_ok=True)
    run([sys.executable,'scripts/generate_traces.py'])
    rtl_files=sorted(str(p.relative_to(ROOT)) for p in (ROOT/'rtl').glob('*.v'))
    run(['iverilog','-g2012','-Wall','-s','reset_tb','-o','build/reset_tb',
         *rtl_files,'tb/main_memory.v','tb/reset_tb.sv'])
    reset_output=run(['vvp','build/reset_tb'],'results/reset.log')
    if 'PASS reset:' not in reset_output:
        raise SystemExit('Reset simulation did not finish successfully')
    for cache,block,suffix in [(1024,16,''),(512,32,'_512_32')]:
        binary=f'build/cache_tb{suffix}'
        run(['iverilog','-g2012','-Wall','-s','cache_tb',
             f'-Pcache_tb.CACHE_BYTES={cache}',f'-Pcache_tb.BLOCK_BYTES={block}',
             '-o',binary,*rtl_files,'tb/main_memory.v','tb/cache_tb.sv'])
        for trace in sorted((ROOT/'traces').glob('*.trace')):
            cmd=['vvp',binary,f'+TRACE=traces/{trace.name}',f'+RESULT=results/{trace.stem}{suffix}.csv']
            if trace.stem=='directed' and not suffix:
                cmd+=['+VCD=results/directed.vcd']
            output=run(cmd,f'results/{trace.stem}{suffix}.log')
            if 'PASS requests=' not in output:
                raise SystemExit('Simulation did not finish successfully')
        run([sys.executable,'scripts/analyze.py','--cache-bytes',cache,'--block-bytes',block,'--suffix',suffix])
        import json
        summary=json.loads((ROOT/'results'/f'summary{suffix}.json').read_text())
        for row in summary:
            log=(ROOT/'results'/f"{row['workload']}{suffix}.log").read_text()
            counts=re.search(r'memory_reads=(\d+) memory_writes=(\d+)',log)
            assert counts and tuple(map(int,counts.groups())) == (row['memory_read_words'],row['memory_write_words'])
    run(['iverilog','-g2012','-Wall','-DBASELINE','-s','cache_tb','-o','build/baseline_tb',
         *rtl_files,'tb/main_memory.v','tb/cache_tb.sv'])
    for trace in sorted((ROOT/'traces').glob('*.trace')):
        run(['vvp','build/baseline_tb',f'+TRACE=traces/{trace.name}',
             f'+RESULT=results/{trace.stem}_baseline.csv'],f'results/{trace.stem}_baseline.log')
    run([sys.executable,'scripts/compare_baseline.py'])
    if not args.skip_synthesis:
        run(['yosys','-Q','-T','-s','scripts/synthesize.ys'],'results/synthesis.log')
    print('All requested checks passed. Results are in results/.')

if __name__=='__main__':
    main()
