#!/usr/bin/env python3
"""Prepare a NEW IEEE report draft from current results; never overwrite a report."""
import argparse
import json
from pathlib import Path

R=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,required=True)
a=parser.parse_args()
if a.output.exists(): parser.error('Choose a new output file; edited reports are never overwritten.')
summary=json.loads((R/'results/summary.json').read_text())
baseline=json.loads((R/'results/baseline_comparison.json').read_text())
fpga=json.loads((R/'results/fpga_summary.json').read_text())
generic=json.loads((R/'results/synthesis_stats.json').read_text())['design']
report='''# Design and Verification of a Direct-Mapped Cache Controller

## Abstract
This project implements a blocking direct-mapped cache controller in synthesizable
Verilog. The default cache stores 1 KB of data in 64 lines with 16-byte blocks and
uses 32-bit byte addresses. A seven-state controller supports aligned word reads
and writes using write-through and no-write-allocate. Modular storage, decoding
and tag comparison separate the controller from its datapath. Independent
Verilog and Python reference models check data and hit/miss behavior across
eight workloads and two cache geometries. A no-cache baseline and a mapped FPGA
netlist provide additional comparisons. Repeated reads achieve a 96.88% hit rate
and a 1.826x reduction in mean response latency relative to the baseline.
Reference-device place and route estimates a maximum internal clock frequency
of FMAX MHz. The results quantify locality benefits and show the latency cost
of serial block refill under unfavorable access patterns.

**Index Terms** - Direct-mapped cache, Verilog, memory hierarchy, FPGA, AMAT.

# I. Introduction
A cache can reduce memory-access latency when an access stream reuses data or
visits nearby addresses [1]. Direct mapping assigns each memory block to one
cache line, reducing lookup complexity while exposing conflict misses. The
objective is to implement correct lookup and refill and relate observed hit
rates to explicit timing assumptions. The design is a standalone controller,
not a complete processor. It accepts one outstanding CPU request and exposes a
word-oriented backing-memory interface.

This report presents the architecture, controller behavior, verification
method, baseline comparison and reference FPGA results. The project group has
two actual members: Shaurya Sharma (2401010439) and Lakshay Saharan (2401020034).
The course rubric mentions five members; approval for the smaller group remains
a faculty decision. No additional names or contributions are assumed.

# II. Literature Review
Cornell CS 3410's cache notes describe locality, direct mapping, tag/index/offset
fields, conflict misses and write-policy choices [1]. These concepts motivate
the small cache and the locality/conflict experiments used here. A line's valid
bit prevents an uninitialized entry from appearing to contain a useful block.

Write-through sends every store to backing memory, while no-write-allocate
avoids loading a block on a store miss [1]. This combination removes dirty-block
eviction control but makes write completion depend on memory acknowledgement.
The standard read AMAT model combines hit time with miss rate times additional
miss penalty. This project derives its cycle costs from the actual FSM.

Icarus Verilog documents simulation models and testbenches as a way to exercise
hardware behavior [2]. The project uses separate Verilog and Python oracles.
Yosys describes the synthesis of coarse-grain memory and logic into lower-level
representations [3]. The nextpnr flow adds target-specific placement, routing
and timing analysis [4]. Simulation, generic synthesis and reference-device
timing are reported as distinct forms of evidence.

# III. Proposed Solution
## A. Organization and Address Fields
The cache contains 1024/16 = 64 lines and four 32-bit words per block. The
32-bit address splits into a 22-bit tag, a 6-bit index and a 4-bit byte offset.
The offset consists of two word-selection bits and two byte-selection bits;
supported requests set the lowest two bits to zero.

| Field | Address bits | Width |
|---|---|---:|
| Tag | [31:10] | 22 |
| Index | [9:4] | 6 |
| Word offset | [3:2] | 2 |
| Byte offset | [1:0] | 2 |

Data storage is 8192 bits, tag storage is 1408 bits and valid storage is 64 bits.
These 9664 logical storage bits exclude control registers. For byte address A,
index=(A/16) mod 64 and tag=A/1024, using integer division. Addresses 0 and 1024
therefore share index zero with different tags.

![Fig. 1. System architecture and RTL module boundaries.](assets/architecture.png)

The hierarchy comprises direct_mapped_cache, cache_address_decoder,
cache_tag_comparator, cache_metadata and cache_data_ram. The top module contains
the request registers, FSM and memory interface. The data RAM has a synchronous
read port and a separate synchronous write port, permitting block-RAM inference.
The incoming CPU address selects the RAM word at request acceptance; LOOKUP
uses that registered value on the next edge. Metadata clears valid bits on reset.

## B. State Transitions
Figure 2 shows the seven controller states. IDLE accepts a request and LOOKUP
classifies it. A read hit prepares RESPONSE. A read miss invalidates the victim
and alternates REFILL_REQ with REFILL_WAIT to fetch all words. The final word
installs the tag and valid bit. The requested word is saved for the CPU while
refill continues.

![Fig. 2. Controller state transitions; request/wait states hold until their handshake completes.](assets/fsm.png)

On a write hit, the controller updates the cached word and memory. On a write
miss it updates only memory and preserves the existing cache line. WRITE_REQ
holds the memory request and WRITE_WAIT waits for acknowledgement. RESPONSE
holds data and hit status until CPU acceptance. Write response data is zero.

## C. Interface Contract
A request transfers on a rising edge when valid and ready are both high.
Payload and valid remain stable while ready is low. CPU responses follow the
same rule. The memory returns one registered response pulse per accepted
request, at least one edge later, without a response-ready input. All interfaces
share one clock. Active-high synchronous reset invalidates the cache and aborts
outstanding work; the memory interface must reset or cancel old responses too.

# IV. Experimental Method
The test memory holds 64 KB and initializes word i to 0xA5A50000 XOR i.
It uses five response-latency cycles and rejects requests every fourth model
cycle. The test CPU accepts responses only every fifth cycle. All traces use
aligned word addresses and start from reset.

The eight workloads cover cold reads, every block-word offset, sequential reads,
repeated reads, alternating conflicting blocks, uniform random reads, mixed
reads/writes and a write stream followed by reads. Random generation uses seed
2026. The primary testbench checks every result against independent data/tag
scoreboards, checks stall stability and verifies the complete backing memory.
Python independently reconstructs expected data, tags and traffic from traces.
A dedicated reset test covers warm invalidation, refill abort and held-response
abort. Global timeouts prevent a hung controller from passing.

The two cache configurations (1024/16 and 512/32 bytes) account for 9252 checked
transactions. The no-cache baseline adds 4626 transactions. The synthesized
FPGA primitive netlist adds another 4626 transactions, whose CSVs match the RTL
exactly, including response latency. Thus 18,504 trace transactions pass in
total, in addition to the reset scenarios. The baseline retains the CPU lookup
stage and memory protocol but sends one memory transaction per CPU request.

![Fig. 3. Actual VCD waveform for a cold refill followed by hits.](assets/waveform.png)

The waveform verification script samples stable response values before every
rising clock edge and checks all 18 directed-trace handshakes against the CSV.
The plotted waveform is extracted from the simulator's VCD, not drawn from an
idealized sequence. Tests provide evidence for exercised cases; they are not
an exhaustive formal proof.

# V. Results and Discussion
## A. Hit and Miss Behavior
| Workload | Requests | Hits | Hit rate |
|---|---:|---:|---:|
'''
for row in summary:
    report+=f"| {row['workload']} | {row['requests']} | {row['hits']} | {row['hit_rate']:.2%} |\n"
report+='''
Sequential reads achieve one miss and three hits per block, giving 768/1024
hits, or 75%. The repeated trace fits a 256-byte working set in the cache;
only its first 16 blocks miss, giving 496/512 hits, or 96.875%. Alternating
addresses 0 and 1024 produces a miss on every access. Random references cover
a much larger region and produce little reuse. These finite-trace results do
not claim a universal random-access rate.

## B. AMAT and Baseline Comparison
An ideal read hit takes two cycles from request acceptance to response
acceptance. Each serial memory word adds seven cycles: request/response
sequencing plus the five-cycle memory latency. A four-word read miss therefore
takes 2 + 4 x 7 = 30 cycles; a write takes 2 + 7 = 9 cycles. With R reads,
W writes, RM read misses and N=R+W, the ideal average is:

AMAT = (2R + 28RM + 9W) / N. (1)

For sequential reads, AMAT=2 + (256/1024)x28=9 cycles. Repeated reads give
2.875 cycles and the conflict trace gives 30 cycles. Measured response time also
includes acceptance stalls and CPU response backpressure, but excludes driver
idle gaps. It is not processor CPI or whole-trace throughput.

| Workload | Cache cycles | Baseline cycles | Ratio |
|---|---:|---:|---:|
'''
for name in ['repeated','sequential','conflict','random','mixed']:
    row=next(r for r in baseline if r['workload']==name)
    report+=f"| {name} | {row['cache_response_cycles']:.3f} | {row['baseline_response_cycles']:.3f} | {row['response_speedup']:.3f}x |\n"
report+='''
The ratio is baseline mean response latency divided by cache mean response
latency. Repeated reads benefit, but sequential and conflict accesses are slower
than the baseline. A cache miss transfers four serial words while an uncached
read transfers one. A high hit rate alone therefore does not guarantee a latency
improvement under this memory model.

The alternative 512-byte cache with 32-byte blocks gives 87.5% sequential hits,
but the ideal sequential AMAT remains nine cycles: fewer misses each fetch twice
as many words. Because both capacity and block size change, this comparison does
not isolate either parameter.

## C. Synthesis and Reference FPGA Timing
Generic Yosys synthesis of the modular default cache produces GENERIC generic
cells after flattening and removing scope metadata. These counts are distinct
from FPGA resources. Reference synthesis and routing use an iCE40 HX8K device,
CT256 package, seed 1 and a 25 MHz clock target.

| Reference-device metric | Result |
|---|---:|
| Logic cells | 610 / 7680 (7.94%) |
| Block RAMs | 4 / 32 (12.50%) |
| IO cells | 206 / 206 (100%) |
| Estimated post-route internal Fmax | FMAX MHz |
| Requested clock target | 25 MHz (met) |

The post-route estimate is taken from nextpnr's final JSON report. All IOs are
automatically placed and there are no external input/output delay constraints.
The wide standalone interface consumes all package IO cells; a practical board
integration would need a narrower host interface or an internal CPU connection.
The reported Fmax concerns internal clocked paths for this reference build. It
is not a board measurement or a guarantee of external interface timing. No FPGA
board was supplied, and programming or physical demonstration was not performed.

# VI. Individual Contributions
The group membership and responsibilities below were confirmed by the user.

| Member | Roll number | Responsibilities |
|---|---|---|
| Shaurya Sharma | 2401010439 | RTL, memory model, testbenches, traces, simulation, performance analysis and synthesis |
| Lakshay Saharan | 2401020034 | Report, slides and video preparation |

# VII. Conclusion
The modular cache correctly performs direct-mapped lookup, refill, reset
invalidation and write-through transactions for the tested requests. Independent
reference models, waveform checks and mapped-netlist simulation provide
consistent functional evidence. Locality improves repeated-read response time,
while serial refill exposes the cost of misses. The reference FPGA flow meets
a 25 MHz target and provides measured tool outputs for resource/timing analysis.

Limitations include one outstanding request, aligned words only, no write
buffer, no burst refill, no memory errors and no coherence. Burst transfers and
a write buffer are useful extensions. Reproduce RTL and baseline verification
with python3 scripts/run.py, and reference implementation with
python3 scripts/run_fpga.py. The repository includes the report, demonstration
video, diagrams, source files and raw evidence. Live presentation remains a
student activity.

# References
[1] Cornell University, "Caches," CS 3410, Spring 2026. [Online]. Available:
https://www.cs.cornell.edu/courses/cs3410/2026sp/notes/caches.html

[2] Icarus Verilog, "Simulation Using Icarus Verilog." [Online]. Available:
https://steveicarus.github.io/iverilog/usage/simulation.html

[3] YosysHQ, "Synthesis in detail," Yosys Documentation. [Online]. Available:
https://yosyshq.readthedocs.io/projects/yosys/en/stable/using_yosys/synthesis/index.html

[4] YosysHQ, "nextpnr: FPGA place and route." [Online]. Available:
https://github.com/YosysHQ/nextpnr
'''
report=report.replace('FMAX',f"{fpga['estimated_post_route_fmax_mhz']:.2f}").replace('GENERIC',f"{generic['num_cells']:,}")
a.output.parent.mkdir(parents=True,exist_ok=True)
with a.output.open('x') as f:f.write(report)
print(a.output)
