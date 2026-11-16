# Direct-Mapped Cache Controller

Modern Computer Architecture - B.Tech (CS & AI), Project 6.

A synthesizable, blocking, 1 KB direct-mapped cache with 16-byte blocks,
32-bit byte addresses, aligned 32-bit reads/writes, and write-through /
no-write-allocate. Includes independently checked simulations, deterministic
traces, a memory model with stalls, performance analysis, and generic synthesis.

## Start here

1. Read `docs/REPORT.md` for the architecture and results.
2. Read `docs/DEMO_AND_VIVA.md` to prepare for the demonstration.
3. Run `python3 scripts/run.py` to reproduce the experiment.
4. Open `results/summary.md` for the measured results.
5. Open `results/directed.vcd` in a waveform viewer for the short demo trace.

## Requirements and commands

Requires Python 3 (standard library only for verification), Icarus Verilog
(`iverilog`, `vvp`), and Yosys. On macOS:

```sh
brew install icarus-verilog yosys
python3 scripts/run.py
```

On Ubuntu/Debian:

```sh
sudo apt-get install iverilog yosys python3
python3 scripts/run.py
```

Equivalent: `make`. Simulation without synthesis: `make test`.
The runner stops on a simulation failure, data mismatch, hit/miss mismatch,
incorrect memory traffic, or synthesis error. No FPGA board is required.

## Files

| Path | Purpose |
|---|---|
| `rtl/direct_mapped_cache.v` | Synthesizable cache storage, decode, compare, FSM and memory interface |
| `tb/main_memory.v` | Test-only 64 KB memory, 5-cycle latency and periodic acceptance stalls |
| `tb/cache_tb.sv` | Independent data/tag scoreboard and handshake stability checks |
| `tb/reset_tb.sv` | Reset invalidation and outstanding-transaction cancellation tests |
| `scripts/generate_traces.py` | Eight reproducible access workloads |
| `scripts/analyze.py` | Independent Python oracle and AMAT/statistics calculation |
| `scripts/run.py` | Complete experiment and verification runner |
| `scripts/synthesize.ys` | Generic Yosys synthesis, structural check and statistics |
| `traces/` | Input files: decimal operation, hexadecimal byte address and write data |
| `results/` | Checked transaction CSVs, simulation logs, statistics and waveform |
| `docs/` | Report, architecture/FSM diagrams, demo and viva material |
| `output/` | PDF report and editable presentation |
| `build/` | Regenerable simulator binaries, synthesized netlist and artifact previews |

## Interface contract

A CPU request transfers on a rising edge with `cpu_req_valid && cpu_req_ready`.
The sender holds valid/address/write/data stable until acceptance. A response
transfers with `cpu_rsp_valid && cpu_rsp_ready`; data and hit remain stable under
backpressure. Only one CPU request is outstanding. A write completes after the
backing-memory acknowledgement. Write responses have data zero.

Memory requests use the same valid/ready acceptance rule. Memory returns exactly
one response per accepted request, at least one rising edge later. Memory has
no response-ready signal: it must pulse `mem_rsp_valid` for one clock when the
cache is in its wait state. CPU, cache and memory share the clock. Synchronous,
active-high reset aborts outstanding work; reset the memory interface alongside
the cache so an old response cannot arrive after reset. A production memory
controller must cancel outstanding requests or tag responses accordingly.

Supported parameter configurations use power-of-two cache and block sizes,
at least two lines and at least two words per block, and a positive tag width.
The checked configurations are 1024/16 and 512/32 bytes. Word width is fixed at
32 bits. Misaligned, byte and halfword accesses, memory errors and coherence are
outside this interface. The test memory restricts addresses to 0..65535; the RTL
address path remains 32 bits.

## Synthesis interpretation

`results/synthesis.log` and `results/synthesis_stats.json` are actual generic
Yosys results. Arrays map into flip-flops and logic in this generic flow.
Cell counts are not FPGA LUT/BRAM counts, silicon area, timing closure, power or
maximum clock frequency. A board/device-specific implementation is future work.
The 10 ns testbench clock sets simulation timing only.

## Rebuilding the report and slides

Verification has no Python package dependencies. Artifact builders use the
Codex bundled ReportLab/Matplotlib and JavaScript artifact runtime available on
this machine; their sources are `scripts/build_report.py` and
`scripts/build_slides.mjs`. The Markdown report and all verification sources are
portable. `docs/REPORT.md` can also be exported to PDF with a Markdown editor.

**Student:** Lakshay Saharan — Roll No. 2401020034
Review the design and rerun the commands so you can explain the evidence.
