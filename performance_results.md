# Performance Test Results

Generated: 2026-08-20 18:40 UTC
Environment: Windows-11-10.0.26200-SP0 | Python 3.13.15
Workload: 20 requests per endpoint, 5 concurrent worker(s), 10.0s timeout

> These are client-observed HTTP timings against the locally running services. They include request, application, and database time. They are not a substitute for a production load test.

| Service | Endpoint | Requests | Successes | Failures | Error rate | Avg ms | Median ms | P95 ms | Min ms | Max ms | Throughput req/s | Status codes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| User / Auth Service | `/health` | 20 | 20 | 0 | 0.0% | 39.92 | 14.78 | 122.04 | 8.97 | 122.04 | 117.54 | 200 |
| Event Service | `/health` | 20 | 20 | 0 | 0.0% | 40.38 | 14.91 | 121.48 | 9.7 | 121.48 | 113.15 | 200 |
| Event Service | `/api/events` | 20 | 0 | 20 | 100.0% | unavailable | unavailable | unavailable | unavailable | unavailable | 23.25 | 500 |
| Booking Service | `/health` | 20 | 20 | 0 | 0.0% | 40.23 | 14.63 | 125.63 | 11.04 | 125.63 | 116.59 | 200 |
| Notification Service | `/health` | 20 | 20 | 0 | 0.0% | 36.38 | 14.11 | 106.69 | 9.88 | 106.69 | 120.2 | 200 |
| Review Service | `/health` | 20 | 20 | 0 | 0.0% | 35.08 | 12.84 | 104.69 | 9.2 | 104.69 | 129.31 | 200 |

## Interpretation guidance

Use the P95 column to describe the upper-end response time observed during the test. Report the request count, worker count, timeout, machine, service deployment mode, and error rate alongside the results. Repeat the test with a higher worker count to discuss scalability; do not claim scalability from a single sequential run.
