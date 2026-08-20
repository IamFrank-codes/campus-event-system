# Campus Event System Test Results

Generated: 2026-08-20 20:19:29

> This report contains the exact test commands and complete pytest output for every service. Dependencies are not installed by this runner.

## User/Auth Service

Working directory: `C:\devs\python\campus-event-system\user-service`

**Command:**

```text
C:\devs\python\campus-event-system\user-service\venv\Scripts\python.exe -m pytest -v
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0 -- C:\devs\python\campus-event-system\user-service\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\devs\python\campus-event-system\user-service
plugins: anyio-4.14.2
collecting ... collected 9 items

test_main.py::test_health_check PASSED                                   [ 11%]
test_main.py::test_register_new_user_succeeds PASSED                     [ 22%]
test_main.py::test_register_duplicate_email_fails PASSED                 [ 33%]
test_main.py::test_register_with_short_password_fails_validation PASSED  [ 44%]
test_main.py::test_login_with_correct_credentials_returns_token PASSED   [ 55%]
test_main.py::test_login_with_wrong_password_fails PASSED                [ 66%]
test_main.py::test_protected_route_without_token_fails PASSED            [ 77%]
test_main.py::test_protected_route_with_valid_token_succeeds PASSED      [ 88%]
test_main.py::test_get_nonexistent_user_returns_404 PASSED               [100%]

============================== 9 passed in 3.33s ==============================
```

## Event Service

Working directory: `C:\devs\python\campus-event-system\event-service`

**Command:**

```text
C:\devs\python\campus-event-system\event-service\venv\Scripts\python.exe -m pytest -v
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0 -- C:\devs\python\campus-event-system\event-service\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\devs\python\campus-event-system\event-service
plugins: anyio-4.14.2
collecting ... collected 9 items

test_main.py::test_health_check PASSED                                   [ 11%]
test_main.py::test_create_event_with_valid_organizer_succeeds PASSED     [ 22%]
test_main.py::test_create_event_with_invalid_organizer_fails PASSED      [ 33%]
test_main.py::test_create_event_with_invalid_capacity_fails_validation PASSED [ 44%]
test_main.py::test_list_events_returns_created_events PASSED             [ 55%]
test_main.py::test_list_events_filtered_by_category PASSED               [ 66%]
test_main.py::test_get_nonexistent_event_returns_404 PASSED              [ 77%]
test_main.py::test_update_event_changes_only_given_fields PASSED         [ 88%]
test_main.py::test_delete_event_removes_it PASSED                        [100%]

============================== 9 passed in 1.34s ==============================
```

## Booking Service

Working directory: `C:\devs\python\campus-event-system\booking-service`

**Command:**

```text
C:\devs\python\campus-event-system\booking-service\venv\Scripts\python.exe -m pytest -v
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0 -- C:\devs\python\campus-event-system\booking-service\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\devs\python\campus-event-system\booking-service
plugins: anyio-4.14.2
collecting ... collected 10 items

test_main.py::test_health_check PASSED                                   [ 10%]
test_main.py::test_create_booking_succeeds_when_everything_valid PASSED  [ 20%]
test_main.py::test_create_booking_fails_when_student_invalid PASSED      [ 30%]
test_main.py::test_create_booking_fails_when_event_invalid PASSED        [ 40%]
test_main.py::test_duplicate_booking_by_same_student_fails PASSED        [ 50%]
test_main.py::test_booking_fails_when_event_is_full PASSED               [ 60%]
test_main.py::test_get_student_bookings_returns_their_bookings PASSED    [ 70%]
test_main.py::test_get_event_bookings_returns_attendees PASSED           [ 80%]
test_main.py::test_cancel_booking_frees_up_the_spot PASSED               [ 90%]
test_main.py::test_cancel_nonexistent_booking_returns_404 PASSED         [100%]

============================= 10 passed in 1.80s ==============================
```

## Notification Service

Working directory: `C:\devs\python\campus-event-system\notification-service`

**Command:**

```text
C:\devs\python\campus-event-system\notification-service\venv\Scripts\python.exe -m pytest -v
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0 -- C:\devs\python\campus-event-system\notification-service\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\devs\python\campus-event-system\notification-service
plugins: anyio-4.14.2
collecting ... collected 6 items

test_main.py::test_health_check PASSED                                   [ 16%]
test_main.py::test_send_notification_succeeds PASSED                     [ 33%]
test_main.py::test_user_cannot_send_for_another_user PASSED              [ 50%]
test_main.py::test_list_and_mark_notification_read PASSED                [ 66%]
test_main.py::test_invalid_notification_type_fails_validation PASSED     [ 83%]
test_main.py::test_unverified_user_returns_404 PASSED                    [100%]

============================== 6 passed in 1.21s ==============================
```

## Review Service

Working directory: `C:\devs\python\campus-event-system\review-services`

**Command:**

```text
C:\devs\python\campus-event-system\review-services\venv\Scripts\python.exe -m pytest -v
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0 -- C:\devs\python\campus-event-system\review-services\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\devs\python\campus-event-system\review-services
plugins: anyio-4.14.2
collecting ... collected 10 items

test_main.py::test_health_check PASSED                                   [ 10%]
test_main.py::test_create_review_succeeds PASSED                         [ 20%]
test_main.py::test_create_review_with_rating_above_5_fails_validation PASSED [ 30%]
test_main.py::test_create_review_with_rating_below_1_fails_validation PASSED [ 40%]
test_main.py::test_duplicate_review_by_same_student_fails PASSED         [ 50%]
test_main.py::test_get_event_reviews_returns_all_reviews_for_that_event PASSED [ 60%]
test_main.py::test_average_rating_calculates_correctly PASSED            [ 70%]
test_main.py::test_average_rating_with_no_reviews_returns_none PASSED    [ 80%]
test_main.py::test_delete_review_removes_it PASSED                       [ 90%]
test_main.py::test_delete_nonexistent_review_returns_404 PASSED          [100%]

============================= 10 passed in 1.50s ==============================
```

## Summary

| Service | Passed | Failed | Skipped | Warnings | Status |
|---|---:|---:|---:|---:|---|
| User/Auth Service | 9 | 0 | 0 | 0 | PASSED |
| Event Service | 9 | 0 | 0 | 0 | PASSED |
| Booking Service | 10 | 0 | 0 | 0 | PASSED |
| Notification Service | 6 | 0 | 0 | 0 | PASSED |
| Review Service | 10 | 0 | 0 | 0 | PASSED |

```text
User/Auth Service:     9 passed
Event Service:         9 passed
Booking Service:      10 passed
Notification Service: 6 passed
Review Service:       10 passed
--------------------------------
Total:                44 passed
Warnings:             0
```

Failed tests: 0
Skipped tests: 0
