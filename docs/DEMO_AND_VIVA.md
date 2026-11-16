# Demonstration and viva preparation

## A 7-minute demonstration

1. Explain the goal: use a small cache to avoid repeatedly reading slow memory.
2. Show the 22-bit tag, 6-bit index and 4-bit offset calculation.
3. Show `rtl/direct_mapped_cache.v`: arrays, comparator and seven-state FSM.
4. Run `python3 scripts/run.py`. Show PASS logs, including reset verification.
5. Open `results/directed.vcd` in GTKWave or another VCD viewer. Add `clk`,
   `reset`, `req_valid`, `req_ready`, `req_addr`, `rsp_valid`, `rsp_ready`,
   `rsp_hit`, `rsp_data`, `dut.state`, `mv`, `mr`, `ma`, `rv`, `he`, `me`.
6. Find reads at 0x00000000 and 0x00000004: the first refills four words and
   the second hits. State codes: IDLE=0, LOOKUP=1, REFILL_REQ=2, REFILL_WAIT=3,
   WRITE_REQ=4, WRITE_WAIT=5, RESPONSE=6.
7. Find 0x00000400 then 0x00000000: different tags replace the same line.
8. Find write 0x00000000=DEADBEEF and the following read. Then find the write
   miss at 0x00000800: it does not allocate, so the following read misses.
9. Show `results/summary.md` and explain locality and conflict behavior.
10. Show `results/synthesis_stats.json` and state its generic synthesis scope.

## Questions you should be able to answer

**Why 64 lines?** 1024 bytes / 16 bytes per block = 64.

**Why is the tag 22 bits?** 32 - log2(64) - log2(16) = 22.

**Why byte-addressed if reads are words?** A 32-bit address names a byte.
The lowest two bits choose a byte within a word; supported requests set them to 0.

**What is a hit?** The indexed line is valid and its stored tag equals the
request tag. Comparing tags without checking valid is incorrect after reset.

**Why do addresses 0 and 1024 conflict?** Their blocks differ by 64. Modulo 64,
they have the same index, but their tags differ.

**Why four memory reads per miss?** A 16-byte block contains four 4-byte words.
The controller fetches all four before marking the line valid.

**Why invalidate the victim before refill?** Partial replacement must never
appear as a complete valid block. The design also blocks new CPU requests during refill.

**Why no dirty bits?** Each store reaches memory before the CPU sees completion.
Eviction never needs a write-back.

**Does a write miss replace a line?** No. No-write-allocate sends the store to
memory and preserves the existing cache line. A later read may then miss.

**Does a write hit need memory?** Yes. Write-through updates both cache and memory.
A hit therefore does not imply a two-cycle response for a write.

**Why are repeated reads better than sequential reads?** A 256-byte working set
fits, so only its initial blocks miss. A single sequential pass benefits from
spatial locality, with one miss and three hits per block.

**Why is sequential hit rate 75%?** There are 256 blocks and 1024 word reads.
Misses=256 and hits=768. Hit rate=768/1024.

**Why does random access perform poorly?** Uniform references span 64 KB,
far larger than the 1 KB cache. The finite trace uses seed 2026; its exact rate
is an experimental result, not a universal random-access rate.

**What is AMAT?** For reads in the ideal timing model: hit time + miss rate x
additional miss penalty. Here that is 2 + read_miss_rate x 28 cycles.
Mixed reads/writes need separate write cost because every write waits for memory.

**Why do measured cycles exceed ideal AMAT?** The memory periodically rejects
requests, and the test CPU accepts responses only every fifth cycle.

**Does a larger block always help?** It may improve spatial hits but increases
serial refill time and reduces line count for a fixed capacity. The alternate
experiment changes capacity as well as block size, so it does not isolate either effect.

**Why zero memory bits after Yosys synthesis?** The generic flow converts
memory arrays to flip-flops and multiplexers. The logical storage still exists.

**Is this FPGA timing closure?** No. Generic synthesis checks the RTL and maps
it to generic logic. Device-specific synthesis, placement and routing are needed
for LUT/BRAM counts, area, clock frequency and power estimates.

**How was correctness checked?** Verilog independently predicts data and
hit/miss, checks all 16,384 memory words at completion, counts traffic/events,
and checks stable requests/responses during stalls. Python independently
recomputes expected data, tag state, statistics and traffic from every trace.

**What are the limitations?** One outstanding request, word accesses only,
no write buffer, no burst refill, no memory errors, no coherence and no virtual
address translation. The simulation memory covers 64 KB.

## Suggested preparation order

Understand the directed trace first. Then trace one miss through the FSM by
hand. Reproduce the sequential calculation. Finally explain the write policy
and distinguish logical cache capacity from mapped hardware resources.
