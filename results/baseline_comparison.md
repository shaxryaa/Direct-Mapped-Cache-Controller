# No-cache baseline comparison

Same traces, memory latency, memory ready schedule and CPU response-ready policy. Each run starts from reset.
Speedup is baseline mean response latency divided by cache mean response latency; idle driver gaps are excluded.
The no-cache controller retains the same request/lookup stages for a controlled comparison.

| Workload | Cache cycles | No-cache cycles | Response speedup |
|---|---:|---:|---:|
| all_offsets | 11.488 | 9.008 | 0.784x |
| conflict | 33.988 | 9.008 | 0.265x |
| directed | 16.611 | 9.111 | 0.548x |
| mixed | 23.431 | 9.002 | 0.384x |
| random | 33.587 | 9.002 | 0.268x |
| repeated | 4.932 | 9.004 | 1.826x |
| sequential | 11.497 | 9.002 | 0.783x |
| write_stream | 10.254 | 9.004 | 0.878x |
