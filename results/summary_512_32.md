# Verified performance results

Cache: 512 bytes; block: 32 bytes. Rates include reads and writes.

| Workload | Requests | Hits | Misses | Hit rate | Ideal AMAT (cycles) | Measured response (cycles) |
|---|---:|---:|---:|---:|---:|---:|
| all_offsets | 256 | 224 | 32 | 87.50% | 9.000 | 11.527 |
| conflict | 256 | 0 | 256 | 0.00% | 58.000 | 65.668 |
| directed | 18 | 9 | 9 | 50.00% | 24.944 | 29.111 |
| mixed | 1024 | 61 | 963 | 5.96% | 38.039 | 43.606 |
| random | 1024 | 7 | 1017 | 0.68% | 57.617 | 65.257 |
| repeated | 512 | 504 | 8 | 98.44% | 2.875 | 4.951 |
| sequential | 1024 | 896 | 128 | 87.50% | 9.000 | 11.507 |
| write_stream | 512 | 224 | 288 | 43.75% | 9.000 | 10.264 |

Ideal AMAT excludes memory acceptance stalls and CPU response backpressure. Measured response time includes both.
See docs/REPORT.md for the timing derivation and workload interpretation.
