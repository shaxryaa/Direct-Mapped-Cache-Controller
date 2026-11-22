# Project interview preparation

This guide connects the Direct-Mapped Cache Controller's design decisions to
its source code, experiments and measured results. Both members should be able
to explain the complete request path and then discuss their individual work in
greater detail.

## Explain the project

The project implements a blocking direct-mapped cache controller in Verilog.
The default cache stores 1 KB in 64 lines, with four 32-bit words per line. It
uses write-through and no-write-allocate. Independent reference models check
functional behavior, and experiments compare locality-sensitive performance
with a no-cache baseline. Reference FPGA synthesis and routing provide resource
and internal timing estimates.

## Demonstrate the implementation

Start from the repository root with Python 3, Icarus Verilog and Yosys installed.

```sh
python3 scripts/run.py
```

This regenerates the eight deterministic traces, runs the reset tests, checks
both cache geometries, validates the no-cache baseline and performs generic
synthesis. A successful run ends with `All requested checks passed.`

Follow this sequence while explaining the evidence:

1. Open `docs/assets/architecture.png`. Trace a CPU request through address
   decoding, metadata, comparison, data RAM and the controller.
2. Open `rtl/direct_mapped_cache.v`. Explain the seven state constants, latched
   request fields, module instances and state transitions.
3. Open `results/directed.csv`. Address 0 initially misses; addresses 4, 8 and
   12 hit after the block is loaded. Address 1024 conflicts with address 0.
4. Open `docs/assets/waveform.png`. Identify request acceptance, memory refill,
   response valid and response ready. Explain why a result must remain stable
   while the CPU is not ready.
5. Open `results/summary.json` and `results/baseline_comparison.json`. Compare
   repeated, sequential and conflict workloads. Explain both improvements and
   slowdowns.
6. Open `results/fpga_summary.json`. Explain the resource counts, timing target
   and the distinction between a tool estimate and a board measurement.

The optional reference FPGA flow requires `nextpnr-ice40` in addition to the
functional verification tools:

```sh
python3 scripts/run_fpga.py
```

This synthesizes and routes the reference device and checks the mapped netlist
against all eight default-configuration traces. Run the standard regression
first so the reference RTL CSVs are available for comparison.

## Explain the address fields

For a 32-bit byte address A:

| Quantity | Calculation | Default width |
|---|---|---|
| Block offset | A mod 16 | 4 bits |
| Word within block | (A / 4) mod 4, using integer division | 2 bits |
| Cache index | (A / 16) mod 64, using integer division | 6 bits |
| Tag | A / 1024, using integer division | 22 bits |

The address layout is tag `[31:10]`, index `[9:4]`, word `[3:2]` and byte
`[1:0]`. Aligned word accesses have byte bits `00`.

Addresses 0 and 1024 both select index 0 but have tags 0 and 1. Direct mapping
allows only one of those blocks in that line at a time. Addresses 0, 4, 8 and
12 belong to the same block, so one refill makes all four words available.

The data capacity is 8192 bits. Tags add 64 x 22 = 1408 bits and valid bits add
64 bits, for 9664 logical storage bits before controller registers. The stated
1 KB capacity refers to data only.

## Explain the state machine

| State | Purpose | Exit condition |
|---|---|---|
| IDLE | Accept and latch one CPU request | CPU valid and ready |
| LOOKUP | Check valid bit and tag; classify read or write | Choose hit, refill or write path |
| REFILL_REQ | Present one memory read | Memory accepts request |
| REFILL_WAIT | Store the returned word | Next word, or response after the last word |
| WRITE_REQ | Present the memory write | Memory accepts request |
| WRITE_WAIT | Wait for acknowledgement | Memory response arrives |
| RESPONSE | Hold CPU data and hit status | CPU accepts response |

The requested word is saved when it arrives during refill, but the CPU response
waits until the whole line is loaded. The valid bit is installed only after the
last refill word. This prevents a partial line from being treated as a hit.

Synchronous data RAM begins reading at request acceptance. LOOKUP then uses the
registered word. Valid bits hide uninitialized data RAM contents, so the data
array does not require a reset loop.

## Defend the design choices

**Direct mapping.** Each memory block has one possible cache line. This keeps
lookup and replacement simple, while allowing conflict misses even when other
lines are unused.

**Write-through.** Each write updates backing memory. On a cache hit, it also
updates the cached word. This avoids dirty-bit and write-back eviction logic,
but writes wait for memory acknowledgement.

**No-write-allocate.** A write miss updates memory without fetching a cache
block. The existing indexed line is preserved. A later read to the written
block may miss and refill the updated value from memory.

**Blocking requests.** Only one CPU request is outstanding. This simplifies
control and ordering, at the cost of preventing overlap between independent
requests.

**Shared reset.** Reset clears valid bits and aborts the controller's work.
The memory interface must also reset or cancel old responses so a stale reply
cannot be mistaken for a response to a new request.

## Interpret the results

| Observation | Explanation |
|---|---|
| Sequential hit rate is 75% | Each four-word block produces one cold miss and three hits. |
| Repeated hit rate is 96.875% | Sixteen blocks miss once across 512 reads; the remaining 496 reads hit. |
| Conflict hit rate is 0% | Alternating blocks continually replace each other at index 0. |
| Repeated reads improve latency by 1.826x | Baseline mean response latency divided by cache mean response latency is 9.00390625 / 4.931640625. |
| Sequential reads are slower than the baseline | Serial four-word refill and interface stalls outweigh the benefit of the hits in this memory model. |

The ideal read model excludes memory acceptance stalls and CPU response
backpressure. A hit takes two cycles and a miss takes 30 cycles, giving:

```text
Ideal read AMAT = 2 + miss_rate x 28 cycles
```

Sequential reads therefore have an ideal AMAT of nine cycles; repeated reads
have 2.875 cycles; conflict reads have 30 cycles. Measured response latency
includes interface stalls. It excludes the driver's idle gaps and is not a
measurement of processor CPI or complete application speedup.

Under that ideal read model, the cache beats a nine-cycle uncached read when
its miss rate is below 25%, or its hit rate is above 75%. This threshold belongs
to this latency model; it is not a universal cache rule.

The alternative geometry uses a 512-byte cache and 32-byte blocks. Its sequential
hit rate is 87.5%, but ideal sequential AMAT remains nine cycles because each
miss fetches twice as many words. Both capacity and block size change, so this
experiment does not isolate either parameter.

## Explain what the tests establish

The Verilog scoreboard checks every returned word and hit decision against its
own reference memory and tag state. Python independently checks the recorded
results against the traces. The testbench also verifies backing-memory contents,
hit/miss event counts and payload stability under backpressure.

The transaction total is:

```text
Two RTL geometries:     9,252
No-cache baseline:      4,626
Mapped FPGA netlist:    4,626
Total:                 18,504
```

Dedicated reset tests separately exercise cold start, warm invalidation,
refill abort and held-response abort. The waveform checker compares all 18
directed-trace response handshakes with the checked CSV. These tests cover the
stated scenarios; they are not exhaustive formal verification of every possible
input sequence.

## Explain the FPGA results

The reference target is an iCE40 HX8K, CT256 package, seed 1, with a 25 MHz
constraint. It uses 610 of 7680 logic cells and four of 32 block RAMs. Estimated
post-route internal Fmax is 75.35 MHz.

The 26,075 generic synthesis cells are from a separate generic mapping and are
not comparable one-for-one with FPGA logic cells. The reference design uses all
206 package IO cells, has automatic IO placement and no external IO-delay
constraints. Board integration would need a suitable interface and pin map;
the reported Fmax is an internal tool estimate.

## Prepare individual explanations

**Shaurya Sharma:** walk through the RTL hierarchy, synchronous RAM timing,
refill and write paths, handshake assertions, reset tests, reference models,
AMAT calculations and synthesis flow. Explain one directed transaction directly
from its trace, CSV and waveform.

**Lakshay Saharan:** explain how the report organizes the problem, literature,
proposed solution, experimental method, results and limitations. Walk through
the slides and the demonstration's visual sequence. Explain why the report
includes the baseline slowdown and why FPGA timing is presented as an estimate.

Both members should also answer the following follow-up questions:

- How does a valid bit differ from a tag, and why are both required?
- Why can a write miss preserve the current cache line?
- What prevents the CPU response from changing while ready is low?
- What happens if reset occurs halfway through a refill?
- Why can a higher hit rate still give a slower measured response?
- How would burst refill or a write buffer change the controller?
- What extra structures would a two-way associative cache need?
- Which assumptions would need to change when connecting a real CPU and memory?

For a two-way cache, explain two candidate tags per set, a way-selection mux and
a replacement policy. For a write buffer, explain queued writes, ordering,
read-after-write hazards and buffer-full backpressure. These are proposed
extensions rather than features implemented in the current RTL.
