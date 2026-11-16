#!/usr/bin/env python3
"""Regenerate the report source from verified experiment outputs."""
import argparse
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description='Generate the original report template into a NEW file; never overwrites edited reports.')
parser.add_argument('--output', type=Path, required=True, help='New output path, for example build/report-template.md')
args=parser.parse_args()
destination=args.output.resolve()
if destination == (R/'docs/REPORT.md').resolve():
    parser.error('docs/REPORT.md is the maintained source. Choose another output path.')
if destination.exists():
    parser.error('Output already exists. Choose a new filename to preserve existing work.')
stats=json.loads((R/'results/synthesis_stats.json').read_text())['design']
summary=(R/'results/summary.md').read_text().splitlines()
table='\n'.join(line for line in summary if line.startswith('|'))
report='''# Direct-Mapped Cache Controller
## Modern Computer Architecture - B.Tech (CS & AI)

Project 6 - Architecture, RTL implementation and experimental analysis

A blocking cache with 1 KB data capacity, 16-byte blocks and 32-bit byte addresses.
The implementation supports aligned 32-bit reads and writes using write-through
and no-write-allocate policies.

### Abstract
A cache stores recently accessed memory blocks close to a processor. This
project implements tag lookup, valid-bit handling, block refill and write-through
transactions in synthesizable Verilog. A seven-state controller accepts one CPU
request at a time and tolerates memory acceptance stalls and CPU response
backpressure. Deterministic traces demonstrate spatial and temporal locality,
conflict misses and write behavior. Two independent reference models check
simulation results. A generic Yosys synthesis run provides hardware evidence.

The default experiment produces 75.00% hits for sequential reads, 96.88% for
repeated reads and 0% for alternating conflicting blocks. These outcomes show
how access patterns determine the usefulness of a direct-mapped cache.

### Submission details
Add student name, roll number, institution, faculty and submission date to the
editable source or presentation before final submission.

### Deliverables
Cache RTL; main-memory model; self-checking testbenches; eight access traces;
transaction CSVs and waveform; hit/miss and AMAT analysis; synthesis log and
statistics; presentation; demonstration guide and viva questions.

<!-- pagebreak -->

# 1. Architecture and address derivation
The cache has one possible location for each memory block. The index chooses
a line, and the tag identifies which memory block currently occupies it. A hit
requires both a valid line and a matching tag. This follows the direct-mapped
organization described in Cornell CS 3410 cache notes [1].

| Quantity | Derivation | Value |
|---|---|---|
| Cache data capacity | C | 1024 bytes |
| Block size | B | 16 bytes |
| Number of lines | C / B | 64 |
| Words per block | B / 4 | 4 |
| Offset width | log2(B) | 4 bits |
| Index width | log2(C / B) | 6 bits |
| Tag width | 32 - 6 - 4 | 22 bits |
| Data storage | 64 x 16 x 8 | 8192 bits |
| Tag storage | 64 x 22 | 1408 bits |
| Valid storage | 64 x 1 | 64 bits |
| Total logical array storage | 8192 + 1408 + 64 | 9664 bits |

```text
Address [31:10] = tag (22 bits)
Address [9:4]   = line index (6 bits)
Address [3:2]   = word within block (2 bits)
Address [1:0]   = byte within word (2 bits, must be 00)
```

For byte address A: block=A/16; index=block mod 64; tag=A/1024;
word=(A/4) mod 4. Integer division is used throughout.

### Worked conflict example
Address 0x00000000 has tag 0 and index 0. Address 0x00000400 has tag 1 and
index 0. Accessing these blocks alternately repeatedly replaces line 0 even
though the remaining lines are unused. Direct mapping needs no LRU policy.

### Implementation blocks
The RTL keeps data RAM, tag RAM, valid-bit RAM, decoder, comparator, controller
and memory interface in one module. The logical blocks map to named arrays
and wires. See docs/ARCHITECTURE.md for the block diagram and FSM diagram.
The memory model is a separate simulation-only module.

<!-- pagebreak -->

# 2. Controller behavior and interface
| State | Main action | Completion transition |
|---|---|---|
| IDLE (0) | Accept and latch a CPU request | LOOKUP |
| LOOKUP (1) | Check valid/tag and classify hit/miss | RESPONSE, REFILL_REQ or WRITE_REQ |
| REFILL_REQ (2) | Hold one word-read request | REFILL_WAIT on memory ready |
| REFILL_WAIT (3) | Store returned word | Next request or RESPONSE after last word |
| WRITE_REQ (4) | Hold one word-write request | WRITE_WAIT on memory ready |
| WRITE_WAIT (5) | Wait for write acknowledgement | RESPONSE |
| RESPONSE (6) | Hold CPU data and hit status | IDLE on CPU ready |

### Reads
On a read hit, the selected word becomes the response. On a read miss, the
controller invalidates the victim line, requests every word in ascending order,
and saves the requested word for the CPU. It installs the new tag and valid bit
only when the final word arrives. It serves no new CPU request during refill.

### Writes
A write hit updates the cached word and backing memory. A write miss updates
only memory and preserves the current line. Every write waits for a memory
acknowledgement before responding. Write response data is zero. These choices
implement write-through and no-write-allocate [1]. Dirty bits are unnecessary.

### Handshaking
CPU and memory requests transfer at a rising edge when valid and ready are
both high. A sender must hold valid and payload stable until that edge. CPU
responses follow the same rule. Memory responses use a one-cycle valid pulse
with no response-ready input. The memory must return exactly one response per
request, at least one edge after acceptance. All interfaces share a clock.

### Reset
Synchronous active-high reset clears all valid bits and returns to IDLE. Data
and tag arrays need no reset because invalid entries cannot produce hits.
Reset cancels an outstanding transaction. The cache and memory interface must
reset together or otherwise cancel old responses. The test model resets its
contents to a known pattern for independent experiments.

<!-- pagebreak -->

# 3. Verification method and access traces
The testbench uses separate data and tag scoreboards. It predicts every CPU
response, checks hit/miss status, checks every backing-memory word after a
trace, verifies event counts and checks stable outputs during backpressure.
A Python oracle independently reconstructs the memory contents and cache tags
from each input trace and checks every output CSV transaction and traffic count.

The memory holds 16,384 words (64 KB), starts with word[i]=0xA5A50000 XOR i,
and responds after five latency cycles. Its ready signal stalls every fourth
model cycle. The test CPU accepts responses only every fifth cycle. A global
timeout prevents a stalled controller from silently passing.

| Trace | Requests | Purpose |
|---|---:|---|
| directed | 18 | Cold miss, offsets, conflict, writes and last memory word |
| sequential | 1024 | One 4 KB sequential word-read pass |
| repeated | 512 | Eight passes over a 256-byte working set |
| conflict | 256 | Alternate reads at byte addresses 0 and 1024 |
| random | 1024 | Uniform word reads across 64 KB, seed 2026 |
| mixed | 1024 | Reads/writes over 8 KB, 35% write probability |
| write_stream | 512 | 256 stores followed by 256 reads of the same region |
| all_offsets | 256 | Each word position in every default cache line |

Trace rows contain decimal operation (0 read, 1 write), hexadecimal byte address
and hexadecimal write data. A read ignores the write-data field. Each workload
starts from a reset cache and freshly initialized memory.

### Coverage and observed outcome
All eight traces passed at 1024-byte cache / 16-byte block and again at 512-byte
cache / 32-byte block. That is 9,252 checked transactions across 16 trace runs.
The reset test also passed warm-line invalidation, reset during an outstanding
refill and reset while a CPU response was held. These tests establish evidence
for the tested scenarios, rather than exhaustive formal proof.

The test memory limits addresses to 64 KB, although the RTL address path is
32 bits. Requests are aligned words. Memory errors, byte stores and unaligned
accesses are outside the contract.

<!-- pagebreak -->

# 4. Hit/miss results and architectural analysis
'''+table+'''

### Spatial locality
Sequential reads fetch one new 16-byte block every four word accesses. There
are 256 misses and 768 hits: hit rate=768/1024=75%. The out-of-order word-offset
trace also achieves 75%, demonstrating that refill stores all four words.

### Temporal locality
The repeated trace fits its 256-byte working set inside the cache. Only the
first access to each of its 16 blocks misses: hits=(512-16)/512=96.875%.

### Conflict behavior
Alternating addresses 0 and 1024 repeatedly evicts the same indexed line.
The trace has 256 misses and zero hits. This is a deliberately unfavorable
access pattern that exposes direct mapping's placement restriction.

### Random accesses and writes
Random references cover a region much larger than the cache, so reuse is low.
The observed rate is specific to this finite, seeded trace. In write_stream,
all 256 initial stores miss without allocating. The later reads incur 64 block
misses and 192 hits, giving an overall 37.5% hit rate. Total-access hit rate
therefore differs from read-only hit rate.

### Alternate geometry
With a 512-byte cache and 32-byte blocks, sequential hit rate increases to
87.5% while its ideal AMAT stays at 9 cycles: each miss transfers twice as many
words, but occurs half as often. Repeated-read hit rate becomes 98.4375%.
Both cache capacity and block size change in this experiment, so these results
must not be interpreted as an isolated study of either parameter.

<!-- pagebreak -->

# 5. AMAT and measured timing
AMAT means average memory access time. State the latency assumptions before
using a hit/miss ratio to calculate it. For reads, the usual form is:

```text
AMAT_read = hit_time + read_miss_rate x extra_miss_penalty
```

### Ideal timing model for this implementation
The CPU request is accepted at edge E0. LOOKUP runs at E1. A read hit transfers
its response at E2 if the CPU is ready, so hit_time=2 cycles.

For a memory word, request acceptance to response production takes five cycles.
The cache consumes that registered response one edge later. A further request
edge starts the next word. Each serial word therefore adds 7 cycles to the
ideal read-miss path. Four words add 28 cycles beyond the hit path.

| Request type | Ideal response latency |
|---|---:|
| Read hit | 2 cycles |
| Read miss | 2 + 4 x 7 = 30 cycles |
| Write hit or miss | 2 + 7 = 9 cycles |

A miss follows E0 request, E1 lookup, E2/E9/E16/E23 memory acceptance,
E8/E15/E22/E29 refill consumption and E30 CPU response transfer.
A write follows E0 request, E1 lookup/update, E2 memory acceptance,
E8 acknowledgement consumption and E9 CPU response transfer.

For R reads, W writes, RM read misses and N=R+W:

```text
AMAT_ideal = [2R + 28RM + 9W] / N
Sequential: 2 + (256/1024) x 28 = 9 cycles
Repeated:  2 + (16/512) x 28 = 2.875 cycles
Conflict:  2 + (256/256) x 28 = 30 cycles
```

For another block size, replace 28 with 7 x words_per_block. An all-access miss
ratio cannot be used directly in the read-only formula when writes are present.

### Measured response time
The CSV latency is the number of rising-edge intervals between CPU request
acceptance and CPU response acceptance. It includes memory acceptance stalls
and CPU response backpressure. It excludes driver idle gaps and therefore is
not whole-trace throughput or processor CPI. The table reports both metrics.
The 10 ns simulation clock is a chosen testbench time scale, not a measured
hardware clock limit. No speedup claim is made against an unmeasured baseline.

<!-- pagebreak -->

# 6. Synthesis results and hardware scope
The synthesis script reads only rtl/direct_mapped_cache.v, elaborates the
default configuration, runs generic synthesis, checks the resulting structure,
and writes statistics and a mapped Verilog netlist. The testbench, reference
models and backing memory do not form part of the synthesized cache.

'''+f'''| Metric | Actual generic Yosys result |
|---|---:|
| Total generic cells | {stats['num_cells']:,} |
| Wire bits | {stats['num_wire_bits']:,} |
| Generic mux cells | {stats['num_cells_by_type']['$_MUX_']:,} |
| Enable flip-flop cells ($_DFFE_PP_) | {stats['num_cells_by_type']['$_DFFE_PP_']:,} |
| Remaining abstract memories | {stats['num_memories']} |
'''+'''
The 9,600 enable flip-flops include the 8,192 data bits and 1,408 tag bits.
Other sequential cell types hold valid bits and controller/request state.
The generic flow lowers arrays to flip-flops and selection logic, so zero
remaining abstract memories does not mean that the cache has no storage.
Yosys documents this distinction between coarse-grain memory representations
and fine-grain mapping [3].

### Evidence files
results/synthesis.log records the actual tool run. The JSON statistics are in
results/synthesis_stats.json. build/cache_synth.v is a regenerable mapped
netlist. The run used Icarus Verilog 13.0 and Yosys 0.71+post.

### Interpretation limits
These are generic logic counts. No FPGA family, device, constraints or cell
library was supplied. Thus this project makes no claim about FPGA LUTs, BRAM
usage, silicon area, timing closure, maximum frequency or power. A generic
functional and structural synthesis result satisfies the available hardware
flow; a device-specific flow can extend the project if required by faculty.

### Design limitations and possible extensions
The cache blocks during every miss and write and has no write buffer. Refill
uses single-word transactions rather than bursts. Only aligned word accesses
are supported. Memory faults, coherence and virtual memory are outside scope.
Possible extensions include a write buffer, burst refill, byte enables,
set associativity, and a separately controlled capacity/block-size sweep.
Synchronous RAM primitives would require a deliberate lookup pipeline change.

<!-- pagebreak -->

# 7. Reproduction and conclusion
Run the following from the project directory:

```sh
python3 scripts/run.py
```

The runner regenerates traces, compiles both test configurations, executes
reset and trace checks, independently validates results in Python, and runs
Yosys synthesis. It stops on an error. For simulation alone, use:

```sh
python3 scripts/run.py --skip-synthesis
```

### Expected evidence
- PASS messages in results/*.log, including reset.log.
- Checked per-request hit/data/latency rows in results/*.csv.
- Primary and alternate summaries in results/summary*.md and .json.
- The directed waveform in results/directed.vcd.
- Actual mapped cell counts in results/synthesis_stats.json.

The implementation meets the core objective: correct direct-mapped lookup and
refill with valid-bit handling, plus trace-driven hit/miss analysis and explicit
AMAT assumptions. The experiment demonstrates the benefits of locality and
the vulnerability of direct mapping to conflicting addresses. The write policy
provides correct backing-memory behavior without dirty-block eviction logic.

### References
[1] Cornell University, CS 3410, Caches, Spring 2026. Direct mapping, locality
and write policies.
https://www.cs.cornell.edu/courses/cs3410/2026sp/notes/caches.html

[2] Icarus Verilog, Simulation Using Icarus Verilog. Compilation, simulation
and testbench workflow.
https://steveicarus.github.io/iverilog/usage/simulation.html

[3] YosysHQ, Synthesis in detail. Coarse-grain and fine-grain representations.
https://yosyshq.readthedocs.io/projects/yosys/en/stable/using_yosys/synthesis/index.html

The supplied course brief defines the objective and expected deliverables.
All project performance and synthesis numbers come from the included runs.
'''
destination.parent.mkdir(parents=True, exist_ok=True)
with destination.open('x') as stream:
    stream.write(report)
print(f'Wrote original template to {destination}; maintained report unchanged.')
