#!/usr/bin/env python3
"""Reference-device synthesis, routing, timing and primitive-netlist simulation."""
import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys

R=Path(__file__).resolve().parents[1]

def run(command, log):
    proc=subprocess.run(command,cwd=R,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (R/log).write_text(proc.stdout)
    if proc.returncode:
        print(proc.stdout[-5000:]); raise SystemExit(proc.returncode)

def main():
    for tool in ('yosys','nextpnr-ice40','iverilog','vvp'):
        if not shutil.which(tool): raise SystemExit(f'Missing tool: {tool}')
    (R/'build').mkdir(exist_ok=True); (R/'results').mkdir(exist_ok=True)
    run(['yosys','-Q','-T','-p',
         'read_verilog rtl/*.v; synth_ice40 -top direct_mapped_cache -json build/cache_ice40.json; '
         'write_verilog -noattr build/cache_ice40_netlist.v; stat'], 'results/fpga_synthesis.log')
    run(['nextpnr-ice40','--hx8k','--package','ct256','--json','build/cache_ice40.json',
         '--asc','build/cache_ice40.asc','--report','results/fpga_timing.json',
         '--freq','25','--seed','1','--pcf-allow-unconstrained'],'results/fpga_place_route.log')
    # Find Yosys's installed primitive models without a machine-specific path.
    probe=subprocess.run(['yosys-config','--datdir'],text=True,capture_output=True) if shutil.which('yosys-config') else None
    candidates=[]
    if probe and probe.returncode==0: candidates.append(Path(probe.stdout.strip()))
    candidates += [Path(shutil.which('yosys')).resolve().parent.parent/'share/yosys',
                   Path('/usr/share/yosys'),Path('/usr/local/share/yosys')]
    cells=next((p/'ice40/cells_sim.v' for p in candidates if (p/'ice40/cells_sim.v').exists()),None)
    if cells is None: raise SystemExit('Cannot locate Yosys ice40/cells_sim.v')
    run(['iverilog','-g2012','-DNETLIST','-s','cache_tb','-o','build/fpga_tb',
         'build/cache_ice40_netlist.v',str(cells),'tb/main_memory.v','tb/cache_tb.sv'],
        'results/fpga_netlist_compile.log')
    count=0
    for trace in sorted((R/'traces').glob('*.trace')):
        name=trace.stem
        run(['vvp','build/fpga_tb',f'+TRACE=traces/{trace.name}',f'+RESULT=results/{name}_fpga.csv'],
            f'results/{name}_fpga.log')
        assert 'PASS requests=' in (R/f'results/{name}_fpga.log').read_text()
        with (R/f'results/{name}.csv').open() as f: reference=list(csv.DictReader(f))
        with (R/f'results/{name}_fpga.csv').open() as f: mapped=list(csv.DictReader(f))
        assert reference==mapped, f'{name}: mapped behavior differs from RTL'
        count+=len(mapped)
    report=json.loads((R/'results/fpga_timing.json').read_text())
    clock=next(iter(report['fmax'].values()))
    assert clock['achieved'] >= clock['constraint']
    summary=dict(device='Lattice iCE40 HX8K',package='CT256',seed=1,target_mhz=25,
        estimated_post_route_fmax_mhz=clock['achieved'],utilization=report['utilization'],
        netlist_verified_transactions=count,
        timing_scope='Single-clock internal paths; automatic IO placement, no external input/output delay constraints; reference target only, no board programming.')
    (R/'results/fpga_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
