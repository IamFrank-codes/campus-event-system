# Validation Results

Generated: 2026-08-20 11:44 UTC

## Service health

| Service | URL | HTTP status | Result | Detail |
|---|---|---:|---|---|
| User/Auth Service | `http://127.0.0.1:8001/health` | ERR | FAIL | ConnectionError |
| Event Service | `http://127.0.0.1:8002/health` | ERR | FAIL | ConnectionError |
| Booking Service | `http://127.0.0.1:8003/health` | ERR | FAIL | ConnectionError |
| Notification Service | `http://127.0.0.1:8004/health` | ERR | FAIL | ConnectionError |
| Review Service | `http://127.0.0.1:8005/health` | ERR | FAIL | ConnectionError |

## Test suites

| Service | Folder | Exit code | Result | Summary |
|---|---|---:|---|---|
| User/Auth Service | `user-service` | 0 | PASS | 9 passed, 3 warnings in 4.91s |
| Event Service | `event-service` | 1 | FAIL | 7 failed, 2 passed, 2 warnings in 2.29s |
| Booking Service | `booking-service` | 1 | FAIL | 9 failed, 1 passed, 2 warnings in 2.27s |
| Notification Service | `notification-service` | 0 | PASS | 6 passed, 2 warnings in 2.20s |
| Review Service | `review-services` | 1 | FAIL | 8 failed, 2 passed, 2 warnings in 2.30s |

## Evidence notes

The health section proves whether each service was reachable at the time of testing. The test section records the actual pytest result; do not replace failed results with an earlier claim. If failures are caused by stale unauthenticated fixtures, update the tests and rerun this script.
