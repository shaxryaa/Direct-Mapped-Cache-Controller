# Rubric audit and submission checklist

The technical statuses below describe the prepared LOCAL submission package.
Lakshay's latest GitHub commit, `6ac3947`, updates only `docs/REPORT.md`.
The updated implementation, exported PDF, diagrams, baseline/FPGA evidence and
video still need to be uploaded by a group member. See `PENDING_UPLOADS.md`.
No new commits or pushes were made during this review.

## Required submission links

- Repository: https://github.com/shaxryaa/Direct-Mapped-Cache-Controller
- IEEE report: https://github.com/shaxryaa/Direct-Mapped-Cache-Controller/blob/main/output/pdf/Cache_Controller_Report.pdf
- Direct prototype video: https://raw.githubusercontent.com/shaxryaa/Direct-Mapped-Cache-Controller/main/output/video/Cache_Controller_Demo.mp4
- Video file page: https://github.com/shaxryaa/Direct-Mapped-Cache-Controller/blob/main/output/video/Cache_Controller_Demo.mp4

## IEEE report - 10 marks

| Requirement | Status | Evidence |
|---|---|---|
| IEEE format | Prepared | Four-page Letter PDF, full-width title/authors, two 3.5-inch columns, Times text and numbered sections/citations |
| Abstract | Present | Opening abstract |
| Literature Review | Present | Section II, with verified primary sources |
| Proposed Solution | Present | Section III, address derivation, modular architecture and FSM |
| Individual Contributions | Present | Section VI, both actual members |
| References | Present | Numbered references cited in the report |

This is an IEEE conference-style project report. No course-specific template,
page limit or institution name was provided. If faculty supplies a template,
use it as the final authority. IEEE Xplore/PDF eXpress certification is not claimed.

## Prototype video - 15 marks

| Requirement | Status | Evidence |
|---|---|---|
| Actual video file | Prepared | output/video/Cache_Controller_Demo.mp4 |
| At most five minutes | Verified | 257.81 seconds (4 min 17.81 s), FFprobe evidence in results/video_verification.json |
| Clear project idea | Present | Opening scene explains cache purpose and configuration |
| Introduce all group members | Actual members introduced | Shaurya Sharma, 2401010439, and Lakshay Saharan, 2401020034 |
| Introduce five names | Faculty exception needed | The actual group has two members; three additional identities are not invented |
| Demonstrate working/progress | Present | Actual modular RTL, architecture/FSM, executed PASS logs, waveform, request/result table, baseline and FPGA results |
| Audio and captions | Verified | Synthetic narration, AAC audio stream, WebVTT captions and transcript |

The video is a narrated walkthrough of actual recorded evidence, not a live
desktop recording. It contains synthetic narration, not either member's voice.
If the instructor requires students speaking on camera or a real-time screen
recording, use docs/VIDEO_SCRIPT.md to record that version. No such condition was
stated in the supplied rubric.

## GitHub repository - 5 marks

| Requirement | Status | Evidence |
|---|---|---|
| Report in repository | Source updated; PDF pending upload | Lakshay committed Markdown; matching PDF is prepared locally |
| Prototype video link | Prepared locally; upload pending | MP4, captions and README links are ready locally |
| All prototype implementation files | Updated files pending upload | Modular RTL and verification flows are ready locally |
| Relevant artifacts | Updated artifacts pending upload | Diagrams, waveform, results, timing/resource logs, PPTX and captions are ready locally |
| Version history | Preserved | Original Shaurya and Lakshay commits retained; newer revisions remain local and uncommitted |
| Meaningful contribution from every actual member | Roles documented; faculty review remains | Responsibilities are confirmed by the group, but commit history alone cannot prove every off-repository activity |
| Repository link submitted in course form | Not submitted | The form URL was not supplied |

The earlier Shaurya commit uses a local-machine email, which may not associate
with his GitHub profile. Existing authorship is not rewritten. Each member
should use a GitHub-verified email for their own future substantive changes.
No backdated commits or changes attributed to absent members are created.

## Common requirements

| Requirement | Status | Evidence |
|---|---|---|
| Architecture diagram and explanation | Complete | docs/ARCHITECTURE.md, docs/assets/architecture.png, report Fig. 1 |
| Microarchitecture/state transitions | Complete | Seven-state controller, report Fig. 2, fsm.svg |
| Synthesizable modular RTL | Verified | Top-level controller plus decoder, comparator, metadata and synchronous RAM modules |
| Dedicated directed testbench | Verified | tb/cache_tb.sv, directed.trace, offsets, conflicts and writes |
| Simulation and waveform verification | Verified | Icarus runs, VCD, plot and 18 checked waveform response handshakes |
| Quantitative performance metric | Complete | Hit rates, ideal AMAT, measured latency and baseline response ratio |
| Resource utilization and maximum frequency | Reference-device analysis complete | iCE40 HX8K/CT256: 610 logic cells, 4 RAMs, 75.35 MHz estimated internal post-route Fmax at 25 MHz target |
| Baseline or alternative | Complete | No-cache controller with identical protocol and memory policy; second cache geometry |
| Technical report | Complete | IEEE-style PDF |
| Live demonstration | Student action remaining | Prepared sources, commands, presentation and recording guide |
| Physical FPGA programming | Not performed; no board available | Reference synthesis/place-and-route provided instead |

The FPGA estimate uses seed 1, automatic IO placement and no external delay
constraints. It covers internal clocked paths, not measured board frequency or
external interface timing. All 206 package IOs are occupied by the wide interface;
a practical board integration would need appropriate pin constraints and host wiring.

## Functional evidence totals

- Two cache configurations: 9252 checked transactions.
- No-cache baseline: 4626 checked transactions.
- FPGA primitive netlist: 4626 checked transactions, exactly matching RTL CSVs.
- Total: 18,504 checked trace transactions, plus reset tests.
- Actual VCD: 18 response handshakes independently matched to checked results.

The repeated workload improves mean response latency by 1.826x versus the
baseline. Several other traces are slower because refill transfers four serial
words; the report states this limitation explicitly.

## Remaining external actions

1. Get faculty confirmation that the two-member group satisfies the five-member wording.
2. Review the video, report and members' credits before submission.
3. Paste the repository and video links into the course form; its URL is needed for submission.
4. Deliver the live presentation. Record a human-voiced version only if faculty requires it.
