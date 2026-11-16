#!/usr/bin/env python3
"""Generate architectural diagrams and verify/plot actual VCD handshakes."""
import csv
import json
from pathlib import Path
import subprocess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R=Path(__file__).resolve().parents[1]
A=R/'docs/assets'; A.mkdir(exist_ok=True)
architecture='''digraph architecture {
 graph [rankdir=TB,bgcolor="white",nodesep=.22,ranksep=.30];
 node [shape=box,fontname="Times-Roman",fontsize=11,margin=.10];
 edge [fontname="Times-Roman",fontsize=9];
 cpu [label="CPU: request / response"];
 ctrl [label="direct_mapped_cache\nRequest registers and 7-state controller"];
 dec [label="Address decoder\ntag / index / offset"];
 meta [label="Metadata RAM\n64 tags + valid bits"];
 cmp [label="Tag comparator\nvalid AND tag match"];
 data [label="Data RAM\n256 x 32 bits\nsynchronous read"];
 mem [label="Main-memory interface\nword read / write / acknowledge"];
 cpu -> ctrl [label="valid / ready"];
 ctrl -> dec; dec -> meta; meta -> cmp; dec -> cmp;
 ctrl -> data [label="read / refill / store"];
 cmp -> ctrl [label="hit"];
 ctrl -> mem [label="miss or write"];
 mem -> data [label="refill word"];
 data -> ctrl [label="read data"];
 {rank=same; dec;data;} }
'''
fsm='''digraph fsm {
 graph [rankdir=TB,bgcolor="white",nodesep=.18,ranksep=.28];
 node [shape=box,fontname="Times-Roman",fontsize=11,margin=.08];
 edge [fontname="Times-Roman",fontsize=9];
 IDLE -> LOOKUP [label="CPU accept"];
 LOOKUP -> RESPONSE [label="read hit"];
 LOOKUP -> REFILL_REQ [label="read miss"];
 LOOKUP -> WRITE_REQ [label="write"];
 REFILL_REQ -> REFILL_WAIT [label="memory accept"];
 REFILL_WAIT -> REFILL_REQ [label="more words"];
 REFILL_WAIT -> RESPONSE [label="last word: install"];
 WRITE_REQ -> WRITE_WAIT [label="memory accept"];
 WRITE_WAIT -> RESPONSE [label="acknowledge"];
 RESPONSE -> IDLE [label="CPU accept",constraint=false];
 {rank=same;REFILL_REQ;WRITE_REQ;}
 {rank=same;REFILL_WAIT;WRITE_WAIT;}
}
'''
for name,source in [('architecture',architecture),('fsm',fsm)]:
    (A/f'{name}.dot').write_text(source)
    for ext in ['svg','png']:
        subprocess.run(['dot',f'-T{ext}','-Gdpi=220',str(A/f'{name}.dot'),'-o',str(A/f'{name}.{ext}')],check=True)

# Sample the values immediately BEFORE each rising edge, as the RTL does.
lines=(R/'results/directed.vcd').read_text().splitlines()
scope=[]; names={}; start=0
for i,line in enumerate(lines):
    parts=line.split()
    if line.startswith('$scope'): scope.append(parts[2])
    elif line.startswith('$upscope'): scope.pop()
    elif line.startswith('$var') and scope==['cache_tb']: names[parts[4]]=parts[3]
    elif line.startswith('$enddefinitions'): start=i+1; break
selected=['clk','req_ready','req_valid','rsp_valid','rsp_ready','rsp_hit','rsp_data','rv','mv']
values={}; group={}; time=0; samples=[]; responses=[]
def number(value):
    return int(value,2) if value and not any(c in value.lower() for c in 'xz') else 0

def flush():
    previous=values.copy(); values.update(group)
    if number(previous.get(names['clk'],'0'))==0 and number(values.get(names['clk'],'0'))==1:
        if number(previous.get(names['rsp_valid'],'0')) and number(previous.get(names['rsp_ready'],'0')):
            responses.append((number(previous.get(names['rsp_hit'],'0')),number(previous.get(names['rsp_data'],'0'))))
    samples.append((time/1000,{name:number(values.get(names[name],'0')) for name in selected}))
    group.clear()
for line in lines[start:]:
    if line.startswith('#'):
        flush(); time=int(line[1:])
    elif line.startswith('b'):
        val,identifier=line[1:].split(); group[identifier]=val
    elif line and line[0] in '01xz': group[line[1:]]=line[0]
flush()
with (R/'results/directed.csv').open() as f: rows=list(csv.DictReader(f))
assert responses==[(int(r['hit']),int(r['data'],16)) for r in rows], 'VCD response sequence differs from CSV'
(R/'results/waveform_verification.json').write_text(json.dumps(dict(
    source='results/directed.vcd',checked_response_handshakes=len(responses),
    result='PASS',method='Sample stable valid/ready/hit/data before each clock rising edge; compare every response to directed.csv'),indent=2)+'\n')
plot_signals=['req_valid','req_ready','rsp_valid','rsp_ready','rsp_hit','mv','rv']
fig,axes=plt.subplots(len(plot_signals),1,figsize=(10.5,5.0),sharex=True)
for ax,name in zip(axes,plot_signals):
    points=[(t,v[name]) for t,v in samples if t<=520]
    ax.step([x[0] for x in points],[x[1] for x in points],where='post',color='#087f8c',lw=1.5)
    ax.set_ylim(-.2,1.2);ax.set_yticks([0,1]); ax.set_ylabel(name,rotation=0,ha='right',va='center',fontsize=9)
    ax.spines[['top','right']].set_visible(False);ax.grid(axis='x',alpha=.2)
axes[-1].set_xlabel('Simulation time (ns)');axes[-1].set_xlim(0,520)
fig.suptitle('Actual directed-trace waveform: cold refill followed by cache hits',fontsize=12)
fig.tight_layout();fig.savefig(A/'waveform.png',dpi=220);plt.close(fig)
print(f'PASS: {len(responses)} actual VCD responses match directed.csv; diagrams generated.')

# A fixed scientific layout keeps all state labels and edges legible in one column.
from matplotlib.patches import Rectangle, FancyArrowPatch
fig,ax=plt.subplots(figsize=(9,10));ax.set_xlim(0,9);ax.set_ylim(0,10);ax.axis('off')
nodes={'IDLE':(4.5,9.3),'LOOKUP':(4.5,7.7),'REFILL_REQ':(2.1,5.9),
       'REFILL_WAIT':(2.1,3.9),'WRITE_REQ':(6.6,5.9),'WRITE_WAIT':(6.6,3.9),'RESPONSE':(4.5,1.5)}
for label,(x,y) in nodes.items():
    ax.add_patch(Rectangle((x-1.05,y-.42),2.1,.84,facecolor='white',edgecolor='black',lw=1.5))
    ax.text(x,y,label,ha='center',va='center',fontsize=18)
def route(points,label=None,at=None,rotation=0):
    for a,b in zip(points[:-2],points[1:-1]): ax.plot([a[0],b[0]],[a[1],b[1]],color='black',lw=1.4)
    ax.add_patch(FancyArrowPatch(points[-2],points[-1],arrowstyle='-|>',mutation_scale=17,lw=1.4,color='black'))
    if label: ax.text(*at,label,ha='center',va='center',fontsize=16,rotation=rotation,
                     bbox=dict(facecolor='white',edgecolor='none',pad=1))
route([(4.5,8.88),(4.5,8.12)],'CPU accept',(5.5,8.5))
route([(3.45,7.7),(2.1,7.7),(2.1,6.32)],'read miss',(2.1,7.1))
route([(5.55,7.7),(6.6,7.7),(6.6,6.32)],'write',(6.6,7.1))
route([(4.5,7.28),(4.5,1.92)],'read hit',(4.5,5.0),90)
route([(2.1,5.48),(2.1,4.32)],'mem accept',(2.1,4.9))
route([(6.6,5.48),(6.6,4.32)],'mem accept',(6.6,4.9))
route([(1.05,3.9),(.3,3.9),(.3,5.9),(1.05,5.9)],'more',(.3,4.9),90)
route([(2.1,3.48),(2.1,1.5),(3.45,1.5)],'last word',(2.1,2.6))
route([(6.6,3.48),(6.6,1.5),(5.55,1.5)],'ack',(6.6,2.6))
route([(5.55,1.5),(8.6,1.5),(8.6,9.3),(5.55,9.3)],'CPU accept',(8.6,7.5),90)
fig.subplots_adjust(left=.015,right=.985,bottom=.015,top=.985)
fig.savefig(A/'fsm.png',dpi=220);fig.savefig(A/'fsm.svg');plt.close(fig)
