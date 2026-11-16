# Prototype video transcript

Synthetic narration over actual recorded prototype evidence. Actual group: Shaurya Sharma and Lakshay Saharan.

## 00:00:00.000 - Project idea and group members
A direct-mapped cache controller stores recently used memory blocks to reduce repeated access latency. This prototype uses one kilobyte of cache data and sixteen-byte blocks. The actual group members are Shaurya Sharma, roll number 2401010439, and Lakshay Saharan, roll number 2401020034. Shaurya handles implementation and analysis. Lakshay handles the report, slides and video. This walkthrough uses synthetic narration and actual recorded simulation evidence.

## 00:00:34.149 - System architecture
The cache sits between a CPU request interface and backing memory. The address decoder separates a twenty-two-bit tag, six-bit index and four-bit offset. Metadata stores tags and valid bits. The comparator checks for a hit. Data RAM holds four words per line. Requests and responses use valid and ready handshakes. The controller supports one outstanding CPU request.

## 00:00:57.401 - Synthesizable modular Verilog
This is the actual Verilog implementation. The top module instantiates the decoder, metadata storage, tag comparator and data RAM. The data RAM has synchronous read and write ports, so the FPGA flow can infer block memories. A word is read when the CPU request is accepted, then LOOKUP uses that registered word. The dedicated test memory is excluded from cache synthesis.

## 00:01:21.335 - Seven-state controller
IDLE accepts a request and LOOKUP checks the line. A read hit prepares a response. A read miss alternates REFILL REQUEST and REFILL WAIT until all four words arrive, then installs the tag and valid bit. Writes use write-through with no-write-allocate. A write hit updates cache and memory; a write miss updates memory only. The response waits until the CPU accepts it.

## 00:01:42.957 - Actual verification output
These PASS lines come from the executed testbench. Eight workloads run on two cache configurations. Independent Verilog and Python scoreboards check hit decisions and data. The testbench also checks backing memory and stable outputs during stalls. Reset tests cover invalidation and aborted transactions. Including the no-cache baseline and FPGA primitive netlist, eighteen thousand five hundred and four trace transactions passed.

## 00:02:09.144 - Waveform verification
This waveform comes directly from the simulator V C D file. The first read misses and causes four memory responses before the CPU response becomes valid. Later accesses to other words in the same block hit. CPU response backpressure keeps the result stable until ready. A separate checker samples every directed-trace response handshake and confirms that all eighteen match the checked result C S V.

## 00:02:33.067 - Directed requests and returned data
Here are actual requests from the directed trace. The first read at address zero misses. Reads at four, eight and twelve hit because the whole block was refilled. Address hexadecimal four hundred maps to the same line with a different tag, causing a conflict. Later writes and reads verify write-through and no-write-allocate behavior. Every returned word and hit flag matches the independent model.

## 00:02:55.594 - Measured hit rates and baseline
Sequential reads achieve seventy-five percent hits. Repeated reads over a small working set achieve ninety-six point eight eight percent. Alternating conflicting addresses achieve zero percent. The no-cache comparison is important: repeated reads are about one point eight three times faster, but sequential and conflict accesses are slower with this cache. A miss fetches four serial words while an uncached read fetches only one.

## 00:03:20.752 - Reference FPGA results
The reference implementation targets a Lattice ice forty H X eight K, C T two fifty-six device. It uses six hundred and ten logic cells and four block memories. The post-route internal maximum frequency estimate is 75.35 megahertz, meeting the requested twenty-five megahertz target. IO pins are placed automatically, without external delay constraints. These are tool estimates, not measurements from a physical board.

## 00:03:47.451 - Reproduction and submission
The repository contains the modular source code, testbenches, traces, waveform, raw results, IEEE-format report and this demonstration video. Run python three scripts slash run dot py to reproduce functional verification. Run scripts slash run underscore F P G A dot py for reference synthesis and timing. The actual group has two members, so the five-member rubric requirement needs faculty confirmation. A live presentation remains the group members responsibility.
