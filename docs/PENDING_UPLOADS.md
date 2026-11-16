# Latest repository review and pending uploads

Inventory prepared against `origin/main` at `6ac39478a66fe53d814079cfe7996062c9993a10`, before the submission changes were committed. The lists below record what was missing at that review point.

## What Lakshay committed

`6ac3947` updates only `docs/REPORT.md`: both authors, IEEE sections, modular architecture, baseline results, FPGA resources/Fmax, contributions and references.
It does not upload the corresponding RTL modules, baseline/FPGA scripts and evidence, diagrams, regenerated PDF or demo video.

## Completed locally in this review

- Used Lakshay's report as the source, retaining his wording and tables.
- Added architecture, FSM and actual-waveform figures and exported the matching IEEE-style PDF.
- Re-ran RTL/cache/baseline verification and the reference FPGA/netlist flow.
- Checked the existing 4:18 demonstration, captions, members and artifact consistency.
- Refreshed the submission archive and this upload inventory.
- Preserved the deletion of CONTRIBUTIONS.md, team.json and DEMO_AND_VIVA.md.

## Upload priorities

1. Updated modular `rtl/`, `tb/`, and reproduction scripts with current `results/` evidence.
2. Report source, matching PDF, `docs/assets/` diagrams and current PPTX.
3. MP4, captions and transcript under `output/video/` and `docs/VIDEO_SCRIPT.md`.
4. README, submission checklist, optional CI workflow and complete ZIP.
5. Preserve the intentional file deletions listed below.

The original `.git` history, `build/` caches, and extracted `output/Cache_Controller_Project/` folder do not need uploading. The ZIP is the refreshed complete package.

## New files not present in origin/main

- `.gitattributes`
- `.github/workflows/verify.yml`
- `docs/SUBMISSION_CHECKLIST.md`
- `docs/VIDEO_SCRIPT.md`
- `docs/assets/README.md`
- `docs/assets/architecture.dot`
- `docs/assets/architecture.png`
- `docs/assets/architecture.svg`
- `docs/assets/fsm.dot`
- `docs/assets/fsm.png`
- `docs/assets/fsm.svg`
- `docs/assets/waveform.png`
- `output/video/Cache_Controller_Demo.mp4`
- `output/video/Cache_Controller_Demo.vtt`
- `requirements-artifacts.txt`
- `results/all_offsets_baseline.csv`
- `results/all_offsets_baseline.log`
- `results/all_offsets_fpga.csv`
- `results/all_offsets_fpga.log`
- `results/baseline_comparison.json`
- `results/baseline_comparison.md`
- `results/conflict_baseline.csv`
- `results/conflict_baseline.log`
- `results/conflict_fpga.csv`
- `results/conflict_fpga.log`
- `results/directed_baseline.csv`
- `results/directed_baseline.log`
- `results/directed_fpga.csv`
- `results/directed_fpga.log`
- `results/fpga_netlist_compile.log`
- `results/fpga_place_route.log`
- `results/fpga_run.log`
- `results/fpga_summary.json`
- `results/fpga_synthesis.log`
- `results/fpga_timing.json`
- `results/mixed_baseline.csv`
- `results/mixed_baseline.log`
- `results/mixed_fpga.csv`
- `results/mixed_fpga.log`
- `results/random_baseline.csv`
- `results/random_baseline.log`
- `results/random_fpga.csv`
- `results/random_fpga.log`
- `results/repeated_baseline.csv`
- `results/repeated_baseline.log`
- `results/repeated_fpga.csv`
- `results/repeated_fpga.log`
- `results/sequential_baseline.csv`
- `results/sequential_baseline.log`
- `results/sequential_fpga.csv`
- `results/sequential_fpga.log`
- `results/submission_verification.json`
- `results/video_verification.json`
- `results/waveform_verification.json`
- `results/write_stream_baseline.csv`
- `results/write_stream_baseline.log`
- `results/write_stream_fpga.csv`
- `results/write_stream_fpga.log`
- `rtl/cache_address_decoder.v`
- `rtl/cache_data_ram.v`
- `rtl/cache_metadata.v`
- `rtl/cache_tag_comparator.v`
- `rtl/no_cache_controller.v`
- `scripts/build_demo_video.py`
- `scripts/build_figures.py`
- `scripts/check_pending_uploads.py`
- `scripts/compare_baseline.py`
- `scripts/package_project.py`
- `scripts/prepare_ieee_source.py`
- `scripts/run_fpga.py`
- `scripts/verify_submission.py`

## Existing files with prepared changes

- `.gitignore`
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/REPORT.md`
- `output/Cache_Controller_Project.zip`
- `output/pdf/Cache_Controller_Report.pdf`
- `output/presentation/Direct_Mapped_Cache_Slides.pptx`
- `results/all_offsets.log`
- `results/all_offsets_512_32.log`
- `results/conflict.log`
- `results/conflict_512_32.log`
- `results/directed.log`
- `results/directed.vcd`
- `results/directed_512_32.log`
- `results/mixed.log`
- `results/mixed_512_32.log`
- `results/random.log`
- `results/random_512_32.log`
- `results/repeated.log`
- `results/repeated_512_32.log`
- `results/run.log`
- `results/sequential.log`
- `results/sequential_512_32.log`
- `results/synthesis.log`
- `results/synthesis_stats.json`
- `results/write_stream.log`
- `results/write_stream_512_32.log`
- `rtl/direct_mapped_cache.v`
- `scripts/build_report.py`
- `scripts/build_slides.mjs`
- `scripts/run.py`
- `scripts/synthesize.ys`
- `scripts/write_report_source.py`
- `tb/cache_tb.sv`

## Intentional deletions to preserve

- `docs/DEMO_AND_VIVA.md`

## External actions still needed

- The prepared changes are included in the submission commit under Shaurya Sharma. Push that commit to GitHub to publish the files.
- Obtain faculty confirmation of the actual two-member group against the five-member wording.
- Submit the repository/video links in the course form (its URL has not been provided).
- Deliver the live presentation; no physical FPGA board was supplied.
