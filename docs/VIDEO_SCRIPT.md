# Prototype video transcript

Human narration by Shaurya Sharma and Lakshay Saharan. Approved video: approximately 4 minutes 47 seconds. Captions use speech timestamps; minor recognition errors may remain.

## 00:00:01.670
Hello, I am Shaurya Sharma. I worked on Verilog implementation, test benches,

## 00:00:13.950
simulation and performance analysis and synthesis.

## 00:00:17.910
Hello, I'm Lakshay Saharan.

## 00:00:19.990
I worked on the project report, presentation slides, and the demonstration

## 00:00:23.750
video. Our project studies how a cache between the CPU and the main memory

## 00:00:28.610
handles, requests, and the benefits from the locality.

## 00:00:33.150
The cache stores 1 kilobyte of data using 16 byte blocks.

## 00:00:37.950
Our report explains the design, verification method, measured results,

## 00:00:42.790
and the limitations. Shaurya will now demonstrate the implementations.

## 00:00:47.720
The cache has 64 lines with 4 32 bits words per line, each 32 bit address

## 00:00:54.720
contains a 22 bit tag, a 6 bit index and a 4 bit offset.

## 00:01:00.660
The index selects a line, a hit occurs when its valid bit is set and store

## 00:01:05.140
tag matches the request tag.

## 00:01:07.420
I divided the implementation into an address decoder, tag comparator,

## 00:01:13.160
metadata storage, data ram and controller.

## 00:01:15.920
Requests and responses use valid ready handshakes, the controller handles

## 00:01:21.580
one CPU request at a time.

## 00:01:24.660
The controller uses seven states.

## 00:01:28.240
IDLE accepts the request and lookup checks for a hit.

## 00:01:33.580
A read hit returns the cached word.

## 00:01:36.220
A read miss fetches all four words from memory, then marks the completed

## 00:01:42.360
line valid. The write policy is write through with no write allocate.

## 00:01:48.280
A write hit updates both cache and memory.

## 00:01:51.500
A write miss updates memory without loading a new cache block.

## 00:01:56.280
The responses stay stable until the CPU accepts it.

## 00:02:01.100
Reset clears the valid bits and cancels the outstanding work when the

## 00:02:05.140
memory interface resets along the cache.

## 00:02:08.770
These are actual simulation results.

## 00:02:12.590
Independent Verilog and Python reference models check return data and

## 00:02:17.750
hit or miss decisions.

## 00:02:20.390
Tests also cover writes, conflicting addresses, responses, stalls and

## 00:02:24.750
reset. In this direct trace, address 0 initially misses.

## 00:02:30.390
Reads at address 4, 8 and 12 then hit because the first request loads

## 00:02:35.350
the entire block. Address 1024 maps to the same cache line and cause a

## 00:02:41.310
conflict miss. The waveform show a refill and the response handshakes.

## 00:02:46.630
Across both cache and configurations, the baseline FPGA netlist 18,504

## 00:02:54.110
trace transactions passed plus separate reset tests.

## 00:03:00.500
Sequential reads achieved a 75% hit rate.

## 00:03:05.200
Repeated reads achieved 96.88% while alternating conflicting addresses

## 00:03:11.780
produce 0% hits.

## 00:03:15.080
Repeated reads were about 1.83 times faster than the no-cache baseline

## 00:03:21.500
in the mean response latency.

## 00:03:24.220
Sequentially and conflict access were slower because each cache miss fetches

## 00:03:30.520
four words serially. Reference synthesis and routing for a Lattice iCE40

## 00:03:36.860
HX8K uses 610 logic cells and 4 block RAMs.

## 00:03:44.980
The estimated internal maximum frequency was 75.35 MHz meeting the 25

## 00:03:53.520
MHz target. These are tool estimates.

## 00:03:57.720
We did not test a physical FPGA board.

## 00:04:00.870
The IEEE style report includes the abstract, literature review, proposed

## 00:04:06.730
solution, individual contributions and references.

## 00:04:11.070
It also presents the architecture, state machine, waveform and performance

## 00:04:16.250
comparison. The slide summarizes the results for the demonstration.

## 00:04:22.350
The repository contains our Verilog modules, test benches, access traces,

## 00:04:27.710
simulation evidence, report and presentation.

## 00:04:29.970
Our results show that locality improves repeated access performance while

## 00:04:37.090
conflict misses and serial refill can increase latency.

## 00:04:42.570
Possible improvements include burst refill and write buffer. Thank you.
