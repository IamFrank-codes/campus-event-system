# Performance Test Results

Generated: 2026-08-20 14:21 UTC
Environment: Windows-11-10.0.22631-SP0 | Python 3.12.4
Workload: 50 requests per endpoint, 1 concurrent worker(s), 10.0s timeout

> These are client-observed HTTP timings against the locally running services. They include request, application, and database time. They are not a substitute for a production load test.

| Service | Endpoint | Requests | Successes | Failures | Error rate | Avg ms | Median ms | P95 ms | Min ms | Max ms | Throughput req/s | Status codes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| User / Auth Service | `/health` | 50 | 50 | 0 | 0.0% | 12.79 | 14.59 | 26.81 | 3.5 | 27.61 | 76.67 | 200 |
| Event Service | `/health` | 50 | 50 | 0 | 0.0% | 13.73 | 15.12 | 26.96 | 3.9 | 31.54 | 71.57 | 200 |
| Event Service | `/api/events` | 50 | 50 | 0 | 0.0% | 17.87 | 12.33 | 31.82 | 5.82 | 53.13 | 55.19 | 200 |
| Booking Service | `/health` | 50 | 50 | 0 | 0.0% | 13.78 | 10.26 | 29.81 | 3.75 | 30.82 | 71.32 | 200 |
| Notification Service | `/health` | 50 | 50 | 0 | 0.0% | 11.02 | 5.33 | 31.08 | 3.87 | 56.32 | 88.81 | 200 |
| Review Service | `/health` | 50 | 50 | 0 | 0.0% | 13.45 | 15.13 | 29.08 | 4.01 | 30.46 | 73.05 | 200 |

## Interpretation guidance

Use the P95 column to describe the upper-end response time observed during the test. Report the request count, worker count, timeout, machine, service deployment mode, and error rate alongside the results. Repeat the test with a higher worker count to discuss scalability; do not claim scalability from a single sequential run.
