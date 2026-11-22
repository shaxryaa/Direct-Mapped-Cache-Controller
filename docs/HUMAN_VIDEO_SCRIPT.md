# Two-member voice recording script

Target duration: approximately 4 minutes 30 seconds, including short pauses and screen changes. Rehearse once with a timer and keep the final video below five minutes. Timings are targets, not measured recording durations. Speak the quoted text only; screen directions are not narration. Read roll numbers digit by digit.

This script guided the two members' recordings. The approved submission MP4 now uses their human narration; captions and VIDEO_SCRIPT.md have been updated to the final audio.

## 0:00–0:15 — Shaurya: introduction

Show: title slide with both names and roll numbers.

“Hello, I am Shaurya Sharma, roll number 2401010439. Our Modern Computer Architecture project is a Direct-Mapped Cache Controller. I worked on the Verilog implementation, testbenches, simulation, performance analysis and synthesis.”

## 0:15–0:45 — Lakshay: contribution and project idea

Show: title slide, then architecture diagram.

“Hello, I am Lakshay Saharan, roll number 2401020034. I worked on the project report, presentation slides and demonstration video.

Our project studies how a cache between the CPU and main memory handles requests and benefits from locality. The cache stores one kilobyte of data using sixteen-byte blocks. Our report explains the design, verification method, measured results and limitations. Shaurya will now demonstrate the implementation.”

## 0:45–1:25 — Shaurya: architecture and RTL

Show: architecture diagram, address-field table, then RTL hierarchy.

“The cache has sixty-four lines, with four thirty-two-bit words per line. Each thirty-two-bit address contains a twenty-two-bit tag, a six-bit index and a four-bit offset.

The index selects a line. A hit occurs when its valid bit is set and its stored tag matches the requested tag.

I divided the implementation into an address decoder, tag comparator, metadata storage, data RAM and controller. Requests and responses use valid-ready handshakes. The controller handles one CPU request at a time.”

## 1:25–2:05 — Shaurya: controller and write policy

Show: FSM diagram, then relevant controller code.

“The controller uses seven states. IDLE accepts the request, and LOOKUP checks for a hit. A read hit returns the cached word. A read miss fetches all four words from memory, then marks the completed line valid.

The write policy is write-through with no-write-allocate. A write hit updates both cache and memory. A write miss updates memory without loading a new cache block.

The response stays stable until the CPU accepts it. Reset clears valid bits and cancels outstanding work when the memory interface resets alongside the cache.”

## 2:05–2:50 — Shaurya: working prototype and verification

Show: actual simulation PASS logs, directed trace and waveform. Run `python3 scripts/run.py --skip-synthesis` beforehand or demonstrate it live if the recording timing permits; show its completed output.

“These are the actual simulation results. Independent Verilog and Python reference models check returned data and hit-or-miss decisions. Tests also cover writes, conflicting addresses, response stalls and reset.

In this directed trace, address zero initially misses. Reads at addresses four, eight and twelve then hit because the first request loaded the entire block. Address one thousand twenty-four maps to the same cache line and causes a conflict miss.

The waveform shows the refill and response handshakes. Across both cache configurations, the baseline and FPGA netlist, eighteen thousand five hundred and four trace transactions passed, plus separate reset tests.”

## 2:50–3:40 — Shaurya: performance and synthesis

Show: hit-rate table, baseline comparison and FPGA summary.

“Sequential reads achieved a seventy-five percent hit rate. Repeated reads achieved ninety-six point eight eight percent, while alternating conflicting addresses produced zero percent hits.

Repeated reads were about one point eight three times faster than the no-cache baseline in mean response latency. Sequential and conflict accesses were slower because each cache miss fetches four words serially.

Reference synthesis and routing for a Lattice iCE40 HX8K used six hundred and ten logic cells and four block RAMs. The estimated internal maximum frequency was seventy-five point three five megahertz, meeting the twenty-five megahertz target. These are tool estimates; we did not test a physical FPGA board.”

## 3:40–4:25 — Lakshay: report, slides and closing

Show: actual PDF pages, presentation results slide and repository files. End on the repository URL.

“For my part, I prepared the report, slides and video presentation. The IEEE-style report includes the abstract, literature review, proposed solution, individual contributions and references. It also presents the architecture, state machine, waveform and performance comparison.

The slides summarize these results for the demonstration. The repository contains our Verilog modules, testbenches, access traces, simulation evidence, report and presentation.

Our results show that locality improves repeated-access performance, while conflict misses and serial refill can increase latency. Possible improvements include burst refill and a write buffer. Thank you.”

## Recording notes

- Record each section separately in a quiet room. Leave one or two seconds of silence before and after speaking.
- Use the same microphone and distance where possible. Keep both voices at a similar volume.
- Say “iCE40” as “ice forty,” “RTL” as individual letters, and “megahertz” for MHz.
- Do not read commands, filenames, headings or screen directions aloud.
- Follow the actual contribution split. Neither member needs to claim work performed by the other.
- Screen transitions and narration need retiming for the new recordings. Recreate captions from the final human audio; do not reuse the old timestamps unchanged.
