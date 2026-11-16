# Verified performance results

Cache: 1024 bytes; block: 16 bytes. Rates include reads and writes.

| Workload | Requests | Hits | Misses | Hit rate | Ideal AMAT (cycles) | Measured response (cycles) |
|---|---:|---:|---:|---:|---:|---:|
| all_offsets | 256 | 192 | 64 | 75.00% | 9.000 | 11.488 |
| conflict | 256 | 0 | 256 | 0.00% | 30.000 | 33.988 |
| directed | 18 | 9 | 9 | 50.00% | 14.056 | 16.611 |
| mixed | 1024 | 103 | 921 | 10.06% | 20.512 | 23.431 |
| random | 1024 | 14 | 1010 | 1.37% | 29.617 | 33.587 |
| repeated | 512 | 496 | 16 | 96.88% | 2.875 | 4.932 |
| sequential | 1024 | 768 | 256 | 75.00% | 9.000 | 11.497 |
| write_stream | 512 | 192 | 320 | 37.50% | 9.000 | 10.254 |

Ideal AMAT excludes memory acceptance stalls and CPU response backpressure. Measured response time includes both.
See docs/REPORT.md for the timing derivation and workload interpretation.
