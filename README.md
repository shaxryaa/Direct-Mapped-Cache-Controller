# Direct-Mapped Cache Controller

Modern Computer Architecture - B.Tech (CS & AI), Project 6.

A modular, synthesizable blocking cache with 1 KB data capacity, 16-byte blocks,
32-bit byte addresses, aligned word reads/writes and write-through /
no-write-allocate. Includes independent scoreboards, actual waveform checks,
a no-cache baseline, and reference FPGA resource/timing analysis.

## Submission links

- **Repository:** [Direct-Mapped-Cache-Controller](https://github.com/shaxryaa/Direct-Mapped-Cache-Controller)
- **IEEE report:** [PDF](output/pdf/Cache_Controller_Report.pdf) / [editable Markdown source](docs/REPORT.md)
- **Prototype demonstration:** [MP4](output/video/Cache_Controller_Demo.mp4) / [direct video link](https://raw.githubusercontent.com/shaxryaa/Direct-Mapped-Cache-Controller/main/output/video/Cache_Controller_Demo.mp4)
- **Video captions:** [WebVTT](output/video/Cache_Controller_Demo.vtt) / [transcript](docs/VIDEO_SCRIPT.md)
- **Presentation:** [editable PPTX](output/presentation/Direct_Mapped_Cache_Slides.pptx)
- **Rubric audit and remaining actions:** [submission checklist](docs/SUBMISSION_CHECKLIST.md)

The demonstration uses synthetic narration over actual recorded simulation
evidence. It introduces both actual members and shows source code, diagrams,
PASS logs, waveform, requests/results, baseline comparison and FPGA timing.
It is not a live desktop screen recording. Its duration is measured with FFprobe
and saved in `results/video_verification.json`.

## Actual group and responsibilities

| Member | Roll number | GitHub | Responsibilities |
|---|---|---|---|
| Shaurya Sharma | 2401010439 | [shaxryaa](https://github.com/shaxryaa) | RTL, testbenches, memory model, traces, simulation, analysis and synthesis |
| Lakshay Saharan | 2401020034 | [LakshaySaharan](https://github.com/LakshaySaharan) | Report, slides and video preparation |

The group has **two actual members**. The rubric asks for five names, so faculty
confirmation of the smaller group is still required.

## Reproduce functional verification

Requires Python 3, Icarus Verilog (`iverilog`, `vvp`) and Yosys.

```sh
# macOS
brew install icarus-verilog yosys
python3 scripts/run.py
```

```sh
# Ubuntu/Debian
sudo apt-get install iverilog yosys python3
python3 scripts/run.py
```

Simulation without generic synthesis: `python3 scripts/run.py --skip-synthesis`.
The standard runner checks 9252 cache transactions across two geometries and
4626 no-cache transactions, plus dedicated reset scenarios. It stops on errors.
The standard verification scripts use only Python's standard library.

## Reproduce reference FPGA results

```sh
# macOS
brew install nextpnr-ice40
python3 scripts/run_fpga.py
```

Target: **Lattice iCE40 HX8K, CT256, seed 1, 25 MHz constraint**. The final
post-route report estimates **75.35 MHz internal Fmax**, using **610/7680 logic
cells**, **4/32 RAM blocks** and **206/206 IO cells**. All IOs are automatically
placed, with no external input/output delay constraints. This is a reference
build, not a board measurement. The wide interface uses the whole package IO
budget; physical board integration needs a suitable host interface and pin map.
No board programming was performed.

The FPGA runner additionally simulates the mapped primitive netlist against all
eight traces and checks that all 4626 result rows match the RTL exactly.
Together the flows check **18,504 trace transactions**, plus reset tests.

## Main results

| Workload | Hit rate | Cache response cycles | No-cache response cycles |
|---|---:|---:|---:|
| Repeated | 96.88% | 4.932 | 9.004 |
| Sequential | 75.00% | 11.497 | 9.002 |
| Conflict | 0.00% | 33.988 | 9.008 |

Repeated reads improve mean response latency by **1.826x**. Serial four-word
refill makes misses expensive, so the cache is slower than the baseline for
sequential and conflict traces in this memory model. Hit rate alone does not
establish a latency improvement. See [all performance results](results/summary.md)
and the [baseline comparison](results/baseline_comparison.md).

## Architecture and files

![System architecture](docs/assets/architecture.png)

| Path | Purpose |
|---|---|
| `rtl/direct_mapped_cache.v` | Request registers, seven-state FSM and memory interface |
| `rtl/cache_data_ram.v` | Synchronous data RAM, separate read/write ports |
| `rtl/cache_metadata.v` | Tags and resettable valid bits |
| `rtl/cache_address_decoder.v` | Tag/index/word/block-base decoding |
| `rtl/cache_tag_comparator.v` | Valid and tag equality check |
| `rtl/no_cache_controller.v` | Controlled uncached baseline |
| `tb/cache_tb.sv` | Data/tag scoreboard, stall assertions and memory checks |
| `tb/reset_tb.sv` | Reset invalidation and outstanding-transaction cancellation |
| `tb/main_memory.v` | Test-only 64 KB memory with latency and stalls |
| `scripts/run.py` | Full RTL/baseline regression and generic synthesis |
| `scripts/run_fpga.py` | Device synthesis, place/route and netlist regression |
| `scripts/build_figures.py` | Diagrams, VCD handshake verification and waveform plot |
| `traces/` | Eight deterministic input traces |
| `results/` | Actual checked CSVs, logs, waveform and hardware statistics |
| `docs/` | Maintained report, diagrams, credits, demonstration material and audit |
| `output/` | Submission PDF, PPTX, MP4, captions and ZIP |
| `build/` | Regenerable tools, intermediate frames and mapped netlists (ignored) |

## Interface contract

A CPU request transfers on a rising edge with valid and ready both high. Hold
valid and payload stable until acceptance. CPU responses use the same contract.
Only one request is outstanding. Write responses return zero after backing-memory
acknowledgement. Memory requests use valid/ready and receive one registered
response pulse at least one edge later; there is no memory response-ready input.

All interfaces share one clock. Active-high synchronous reset invalidates the
cache and aborts outstanding work. Reset/cancel the memory interface alongside
the cache so old responses cannot arrive afterward. Supported geometries have
power-of-two sizes, at least two lines, at least two words per block and positive
tag width. Checked geometries are 1024/16 and 512/32 bytes. The simulation memory
covers 64 KB; RTL addresses remain 32 bits. No byte/halfword stores, unaligned
requests, memory-error responses, coherence or virtual memory are implemented.

## Report, figures and video maintenance

`docs/REPORT.md` is the editable source; the PDF is the submission export.
They are two formats of one report. Update the source, then rebuild the export.
Artifact generation needs an optional Python environment:

```sh
python3 -m venv build/artifact-env
build/artifact-env/bin/pip install -r requirements-artifacts.txt
brew install graphviz ffmpeg
build/artifact-env/bin/python scripts/build_figures.py
build/artifact-env/bin/python scripts/build_report.py
build/artifact-env/bin/python scripts/build_demo_video.py  # macOS say narration
python3 scripts/package_project.py
```

The PDF exporter uses IEEE conference-style Letter pages, a full-width title,
two 3.5-inch columns, Times text, numbered section headings and citations. It is
not an IEEE Xplore acceptance or PDF eXpress certification. If faculty supplies
a specific template, use that template as the final authority.

The video builder uses macOS `say` and verifies a duration below 300 seconds.
The PPTX builder uses the bundled artifact runtime. Template-generation
helpers require a NEW output filename and refuse to overwrite the maintained
report. The ZIP packager refuses an outdated PDF and excludes build caches.
